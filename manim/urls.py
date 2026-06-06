from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.execute_code, name='manim_home'),
    path('get_code_text/<int:code_id>/', views.get_code_text, name='get_code_text'),
    path('save_new_code/', views.save_new_code, name='save_new_code'),
    path('save_current_code/', views.save_current_code, name='save_current_code'),
    path('contact/', views.contact, name='contact'),
    path('update-code/', views.update_code, name='update_code'),
    path('set_code_name/', views.set_code_name, name='set_code_name'),
    path('get_code_name/', views.get_code_name, name='get_code_name'),
    path('task-status/<str:task_id>/', views.task_status_view, name='task-status'),
    path('delete_code/<int:code_id>/', views.delete_code, name='delete_code'),
    path('rename_code/<int:code_id>/', views.rename_code, name='rename_code'),
    path('get-share-url/', views.get_share_url, name='get_share_url'),
    path('set-project-visibility/', views.set_project_visibility, name='set_project_visibility'),
    
    path('', include('core.urls')),
]