
from django.core.cache import cache
from urllib3 import request

def save_to_cache(request,code):
    request.session["previous_code"] = code


def get_previous_code(request):
    code = request.session.get("previous_code")
    placeholder_code = '''from manim import *

# enter your manim code here '''
 
    
    return code if code is not None else placeholder_code

#Current Code (A variable to keep track which code is crrently being edited)
     
     
def set_current_code_id(request, code_id):
    request.session["current_code_id"] = code_id

    
def set_current_code_name(request, code_name):
    request.session["current_code_name"] = code_name
    # cache.set('current_code_name', code_name)

def get_current_code_id(request):
    code_id = request.session.get("current_code_id")
    return code_id

def get_current_code_name(request):
    code_name = request.session.get("current_code_name")
    return code_name 
     