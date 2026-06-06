 

import hashlib
import os
import docker
import traceback
import json
import ast
import uuid

from .models import Code 
from .models import ClusterHeartbeat

from .utils import *
from .cache_utils import *

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_q.tasks import async_task
from django_q.models import OrmQ, Task
from django_q.conf import Conf
from datetime import timedelta
from django.utils import timezone

import re
 
print('Manim 21-03-2026 11 46 AM - views.py loaded')

def run_manim_command(image_name, base_dir, media_name, code_filename):
    client = docker.from_env()
    container = None  # Initialize container to None

    # Define the volumes
    volumes = {
        f"{base_dir}/manim/python_code_files": {'bind': '/mnt/code', 'mode': 'ro'},
        f"{base_dir}/media": {'bind': '/mnt/output', 'mode': 'rw'}
    }
    
    # Define the command with the appropriate paths
    docker_command = f"manim -ql /mnt/code/{code_filename} -o /mnt/output/{media_name}"

    # Resource limits
    mem_limit = "600m"     # 3.7gb total system ram
    cpus = 0.8             # max 0.8 of 2 vCPU
    pids_limit = 64        # max processes
    timeout_seconds = 120  # max 2 minutes
    
    try:
        # Run container detached
        container = client.containers.run(
            image=image_name,
            command=docker_command,
            volumes=volumes,
            detach=True,
            user="manimuser",
            # name="manim_container",
            mem_limit=mem_limit,
            nano_cpus=int(cpus * 1e9),  # docker-py uses nanoseconds
            pids_limit=pids_limit,
            network_disabled=True,       # disable network
            security_opt=["no-new-privileges"],
            read_only=False,
            tmpfs={"/tmp": "rw,size=128m"},
            remove=False                  # do not auto-remove, we'll do it manually
        )

        # Wait for the container to finish, with a timeout
        result = container.wait(timeout=timeout_seconds)
        exit_code = result.get('StatusCode', -1)
        
        print(f"EXIT CODE: {exit_code}")

        # Get logs
        logs = container.logs().decode()
        print("=== CONTAINER LOGS ===")
        print(logs)
        

        if exit_code != 0:
            raise Exception(logs)
        return logs
    except docker.errors.ContainerError as e:
        print(f"Container failed: {e}")
        raise
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception as e:
                print(f"Error removing container: {e}")
    
    return logs     



def run_docker_command(media_name, code):
    image_name = 'manimcommunity/manim'
    base_dir = os.path.join(settings.BASE_DIR)
    
    # Create a unique file for this specific task
    code_dir = os.path.join(settings.BASE_DIR, 'manim', 'python_code_files')
    os.makedirs(code_dir, exist_ok=True)
    
    # Use media_name to ensure the python file is as unique as the output
    code_filename = f"{media_name}.py"
    code_filepath = os.path.join(code_dir, code_filename)

    try:
        # Write the code to the unique file
        with open(code_filepath, 'w') as f:
            f.write(code)

        logs = run_manim_command(image_name, base_dir, media_name, code_filename)
        
        # Clean up the code file after execution
        os.remove(code_filepath)

        # On success, return the logs. Django-Q will save this as the task result.
        return logs
    except Exception as e:
        result_message = (
            "Error executing shell command:\n"
            f"{type(e).__name__}: {e}"
        )
        #full traceback for logs:
        full_tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(result_message)
        print("---- FULL TRACE FOR LOG ----")
        print(full_tb)
        raise
    finally:
        # Ensure cleanup happens even if the command fails
        if os.path.exists(code_filepath):
            os.remove(code_filepath)





 




current_code_name = None

def validate_user_input(user_input):
    blacklist = [';', '&', 'rm ', '`', ' sys' , ' os']  
    try:
        for item in blacklist:
            if item in user_input:
                print(f'Blacklisted item: {item}')
                return False
        return True    

    except SyntaxError:
        return False


def cluster_is_running(threshold_seconds=90):
    threshold = timezone.now() - timedelta(seconds=threshold_seconds)
    print(f'Heartbeat detected: {ClusterHeartbeat.objects.filter(last_ping__gt=threshold).exists()}')
    return ClusterHeartbeat.objects.filter(last_ping__gt=threshold).exists() 
 

MAX_QUEUE = 20

def get_queue_size():
    in_queue = OrmQ.objects.count()

    # Ignore tasks running longer than timeout (likely stuck/zombie)
    stale_threshold = timezone.now() - timedelta(seconds=60)  # match timeout
    running = Task.objects.filter(
        started__isnull=False,
        stopped__isnull=True,
        started__gte=stale_threshold   # only count recent ones
    ).count()

    return in_queue + running

def flush_stale_queue():
    stale_threshold = timezone.now() - timedelta(seconds=90)

    # Remove OrmQ entries that a worker locked but never finished (zombie locks)
    OrmQ.objects.filter(lock__lt=stale_threshold).delete()

    # Close out Task records that started but never stopped (zombie tasks)
    Task.objects.filter(
        started__isnull=False,
        stopped__isnull=True,
        started__lt=stale_threshold
    ).update(stopped=timezone.now())

def get_code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()


def execute_code(request):

    saved_codes = Code.objects.filter(user=request.user) if request.user.is_authenticated else None
    
    #saving the entered code
    previous_code = get_previous_code()
    # previous_code = request.POST.get('code', '')

    current_code_name = get_current_code_name()
    
    # Check if the url is a shared code
    is_codeurl = checkurl(request)
    
    if is_codeurl:
        return is_codeurl

    if request.method == 'POST' and request.POST.get('form_type') == 'execute':
        # Health check: Verify that a Q cluster is running
        cluster_alive = cluster_is_running()

        if not cluster_alive:
            # If no cluster is running, return an error message immediately
            context = {
                'result_message': "Error: The processing service is currently unavailable. Please try again later.",
                'previous_code': request.POST.get('code', ''),
                'saved_codes': saved_codes,
                'request': request,
                'current_code_name': current_code_name,
                'cluster_error': True,
            }
            return render(request, 'manim/manim.html', context)

        processsed = False
        #delete old files
        media_dir = os.path.join(settings.BASE_DIR, 'media')

        delete_old_files(media_dir)

        current_code_name = get_current_code_name() # The name of the code opened or created

        #save the code as a python file 
        code = request.POST.get('code', '')
        code_hash = get_code_hash(code)

        previous_code = code
        save_to_cache(previous_code)

        # find class name
        class_name = find_class_name(code) # we need this because the resultant video is saved in a folder named after class name. 
        print(f'class name: {class_name}')
        random_id = uuid.uuid4().hex[:8]
        media_name = f"{class_name}_{random_id}"
        print(f'media_name: {media_name}')
        
        existing = cache.get(code_hash)
        if existing:
            return JsonResponse({"job_id": existing, "status": "already_running"})
        # dont enqueue if the same code is already running. This can happen when user clicks the run button multiple times.
        
        flush_stale_queue()
        #clear stale queue entries before checking queue size, to get a more accurate count and prevent unnecessary rejections due to stuck tasks.

        if get_queue_size() >= MAX_QUEUE:
            print("Queue is full. Cannot process the request at this time.")
            context = {
                'result_message': "Server busy. Too many jobs. Try again in a minute.",
                'previous_code': code,
                'saved_codes': saved_codes,
                'request': request,
                'current_code_name': current_code_name,
                'queue_full': True,
            }
            return render(request, 'manim/manim.html', context)
        

        task_id = async_task('manim.views.run_docker_command', media_name, code)
        print('Docker task started asynchronously')
        print(f'task id: {task_id}')
        result_message = ""

        # print(f'previous code:{previous_code}')        

        #after HTTP request
        context = {'result_message':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
                   'media_name':media_name,
                   'placeholder': False,
                   'saved_codes':saved_codes,
                   'request': request,
                   'current_code_name':current_code_name,
                   'task_id':task_id,
                }
        return render(request, 'manim/manim.html',context)  
         
    #before HTTP request
    placeholder = True
    context = {'previous_code': previous_code,
               'MEDIA_URL': settings.MEDIA_URL,
               'placeholder':placeholder,
               'processed' : False,
               'saved_codes':saved_codes,
               'request': request, 
               'current_code_name':current_code_name,
            }
    return render(request, 'manim/manim.html',context )

@csrf_exempt
def save_new_code(request):
    if request.method == 'POST' and request.POST.get('form_type') == 'save':
        print('save button clicked')
        code_text = request.POST.get('hidden_code_new')
        save_to_cache(code_text)
        is_public = request.POST.get("is_public") == "on"
        name = request.POST.get('name')
        if name:
            # Save the code with the entered name
            code = Code.objects.create(
                user=request.user,
                code_text=code_text,
                name=name,
                is_public=is_public
            )
            set_current_code_id(code.id)            
            set_current_code_name(code.name)
            print('code saved')
            # return redirect('home')  # Redirect to home page or wherever you want
    return redirect('manim_home')  # Redirect back to execute page after saving

    
         

@csrf_exempt  # testing
def save_current_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_code_text = data.get('code_text')

            save_to_cache(new_code_text)
            print(new_code_text)
            
            if not new_code_text:
                return JsonResponse({'status': 'error', 'message': 'Code text is required'}, status=400)

            current_code_id = get_current_code_id()

            if not current_code_id:
                print ("No current Code id") 
                print(f'current_code_name:{current_code_name}')
            
            # Save the code with the entered name
            Code.objects.filter(user=request.user, id=current_code_id).update(code_text=new_code_text)
            print('code saved')
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
 
def get_code_text(request, code_id):
    code = Code.objects.get(id=code_id)
    set_current_code_id(code.id)
    set_current_code_name(code.name)
    print(f'Current code name set as {code.name}') 
    return JsonResponse({'code_text': code.code_text,'code_name':code.name})

def contact(request):
    return render(request, 'contact.html')

# update the django varible 'previous_code' when user opens a code 
@csrf_exempt
def update_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_code = data.get('code_text')
        save_to_cache(new_code) 
        return JsonResponse({'status': 'success', 'code_text': new_code})
    return JsonResponse({'status': 'failed'})


def set_code_name(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)  # Parse JSON data from the request
        code_name = data.get('code_name')

        result = set_current_code_name(code_name)

        # Respond with success
        return JsonResponse({"status": "success", "message": "Code name set successfully", "result": result})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_code_name(request):
    if request.method == "POST":
        import json

        result = get_current_code_name()

        # Respond with success
        return JsonResponse({"status": "success", "message": "Code name set successfully", "result": result})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


def task_status_view(request, task_id):
    task_id = str(task_id)
    if Task.objects.filter(id=task_id).exists():
        task = Task.objects.get(id=task_id)

        if task.success:
            return JsonResponse({'status': 'done'})

        try:
            raw = str(task.result or "")
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': f'could not read result: {e}'})

        lines = raw.strip().splitlines()
        error_line = next(
            (line.strip() for line in reversed(lines) if line.strip()),
            "Unknown error"
        )

        return JsonResponse({'status': 'failed', 'error': error_line})

    if OrmQ.objects.filter(payload__contains=task_id).exists():
        return JsonResponse({'status': 'queued'})

    return JsonResponse({'status': 'processing'})



# delete code
@csrf_exempt
def delete_code(request, code_id):
    if request.method == 'POST':
        try:
            code = Code.objects.get(id=code_id, user=request.user)
            code.delete()
            return JsonResponse({'status': 'success'})
        except Code.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
def rename_code(request, code_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_name = data.get('name', '').strip()
            if not new_name:
                return JsonResponse({'status': 'error', 'message': 'Name cannot be empty'}, status=400)
            code = Code.objects.get(id=code_id, user=request.user)
            code.name = new_name
            code.save()
            return JsonResponse({'status': 'success'})
        except Code.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def checkurl(request):
    share_id = request.GET.get("id")

    if share_id:
        try:
            shared_code = Code.objects.get(
                share_id=share_id
            )

            if not shared_code.is_public:
                return render(
                    request,
                    "manim/manim.html",
                    {
                        "alert_message": "This project is private."
                    }
                )

            previous_code = shared_code.code_text

        except Code.DoesNotExist:
            return render(
                request,
                "manim/manim.html",
                {
                    "alert_message": "Project not found."
                }
            )
        
from django.urls import reverse


def get_share_url(request):

    code_id = get_current_code_id()
    
    print(f"current code id: {code_id}")

    code = Code.objects.get(
        id=code_id,
        user=request.user
    )
    
    url = request.build_absolute_uri(
    reverse("manim_home")
    )
    url += f"?id={code.share_id}"

    return JsonResponse({
        "url": url
    })



