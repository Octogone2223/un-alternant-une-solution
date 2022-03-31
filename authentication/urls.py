from django.urls import path
from . import views
from core import views as app_views


app_name = "authentication"

urlpatterns = [
    path("", app_views.home, name="home"),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path("sign-out/", views.sign_out, name="sign_out"),
    path("user/", views.user, name="user"),
    path("user/password", views.updatePassword, name="changePassword"),
    path("user/cvPublic/<int:id>", views.cvPublic, name="cvPublic"),
    path("user/<int:id>/photo", views.photo, name="photo"),
    path("company/<int:id>/photo", views.company_photo, name="entity"),
    path("school/<int:id>/photo", views.school_photo, name="entity"),
    path("user/forgotPassword", views.forgotPassword, name="forgotPassword"),
]
