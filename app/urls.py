from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path("", views.home, name='home'),
    path("profile", views.profile, name='profile'),
]
