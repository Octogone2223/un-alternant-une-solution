from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_courses, name='list_courses'),
    path('preview/<int:course_id>/', views.preview_course, name='preview_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('create-course/', views.create_course, name='create_course'),
]
