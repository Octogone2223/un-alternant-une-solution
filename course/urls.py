from django.urls import path
from . import views

urlpatterns = [
    # list of courses
    path("", views.list_courses, name="list_courses"),
    # preview of a course (api)
    path("preview/<int:course_id>/", views.preview_course, name="preview_course"),
    # get the details of a course
    path("<int:course_id>/", views.course_detail, name="course_detail"),
    # create a course
    path("create-course/", views.create_course, name="create_course"),
]
