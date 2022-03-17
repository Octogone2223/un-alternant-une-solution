from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views
from app import views as app_views


app_name = 'authentication'

urlpatterns = [
    path('', app_views.home, name="home"),
    path('sign-up/', views.sign_up, name='signup'),
    path('sign-in/', views.sign_in, name='signin'),
    path('sign-out/', views.sign_out, name='signout'),
    path('private-test/', views.private, name='private'),
]
