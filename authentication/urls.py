from django.urls import path
from . import views
from core import views as app_views


app_name = "authentication"

urlpatterns = [
    path("", app_views.home, name="home"),
    # sign up
    path("sign-up/", views.sign_up, name="sign_up"),
    # sign in
    path("sign-in/", views.sign_in, name="sign_in"),
    # sign out
    path("sign-out/", views.sign_out, name="sign_out"),
    # user's profile
    path("user/", views.user, name="user"),
    # user change password
    path("user/password", views.updatePassword, name="changePassword"),
    # user's cv
    path("user/cvPublic/<int:id>", views.cvPublic, name="cvPublic"),
    # user's profile picture
    path("user/<int:id>/photo", views.photo, name="photo"),
    # company's profile picture
    path("company/<int:id>/photo", views.company_photo, name="entity"),
    # school's profile picture
    path("school/<int:id>/photo", views.school_photo, name="entity"),
    # user's forgot password
    path("user/forgotPassword", views.forgotPassword, name="forgotPassword"),
]
