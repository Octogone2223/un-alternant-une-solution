from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # home
    path("", views.home, name="home"),
    # user's profile
    path("profile", views.profile, name="profile"),
    # about page
    path("about", views.about, name="about"),
    # cgu page
    path("cgu", views.cgu, name="cgu"),
    # legal mentions page
    path("legal", views.legal, name="legal"),
    # policy page
    path("policies", views.policies, name="policies"),
    # student details
    path("student/<int:student_id>",
         views.student_detail, name="student_detail"),
    # company details
    path("company/<int:company_id>",
         views.company_detail, name="company_detail"),
    # school details
    path("school/<int:school_id>",
         views.school_detail, name="school_detail"),
]
