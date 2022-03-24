from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path("", views.home, name='home'),
    path("profile", views.profile, name='profile'),
    path("about", views.about, name='about'),
    path("student/<int:student_id>", views.student_detail, name="student_detail"),
    path("company/<int:company_id>", views.company_detail, name="company_detail"),
    path("school/<int:school_id>", views.company_detail, name="school_detail"),


]
