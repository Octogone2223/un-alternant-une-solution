from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views
from app import views as app_views


app_name = 'authentication'

urlpatterns = [
    path('', app_views.home, name="home"),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('private-test/', views.private, name='private'),
]
