from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.list_courses, name='list_courses'),
]
