from http.client import OK, UNAUTHORIZED
import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from authentication.models import School, Student
from course.serializers import (
    CreateCourseSerializer,
)
from .models import Course
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import serializers

# Create your views here.


# get list of courses / formations with filters (optional)
def list_courses(request):
    filters = {}

    # get filters from request and add them to the filters dict
    location = request.GET.get("location", None)
    if location:
        if location.isnumeric():
            filters["school__zip_code"] = location
        else:
            filters["school__city"] = location

    name = request.GET.get("name", None)
    if name:
        filters["name__icontains"] = name

    school = request.GET.get("school", None)
    if school:
        filters["school__name__icontains"] = school

    # get courses from database with filters, only 20 courses at a time
    courses = Course.objects.filter(**filters)[:20]

    # return list of courses page with courses
    return render(request, "list_courses.html", {"courses": courses})


# preview of a course (api)
def preview_course(request, course_id):

    # get course from database by id

    try:
        course = list(
            Course.objects.filter(id=course_id).values(
                "id",
                "name",
                "description",
                "school__name",
                "school__street",
                "school__city",
                "school__zip_code",
            )
        )[0]

        # return the course
        return JsonResponse({"course": course})

    except Course.DoesNotExist:
        return HttpResponseBadRequest("Course not found")


# get the details of a course (must be logged in)
@login_required
def course_detail(request, course_id):
    student = None

    # if user is logged in is a student, get student from database
    if request.user.getUserType() == "Student":
        student = Student.objects.get(user=request.user)

    # if method is PATCH, update the course of the student by the id in the url parameter, save it and return a status code success
    if request.method == "PATCH":
        student.course_id = course_id
        student.save()
        return HttpResponse({"status": "success"}, status=OK)

    # by default, the user is not enrolled in the course
    has_already_enrolled = False

    # check if he has already enrolled in the course and set has_already_enrolled to true if he has
    if student and student.course_id:
        has_already_enrolled = True

    # get course from database by id
    course = Course.objects.get(id=course_id)

    # return the course detail page with the course and the has_already_enrolled boolean, and the student
    return render(
        request,
        "course_detail.html",
        {
            "course": course,
            "has_already_enrolled": has_already_enrolled,
            "student": student,
        },
    )


# create a course (must be logged in as a school)
@login_required
def create_course(request):

    # if method is POST, create a new course
    if request.method == "POST":

        # if user is logged in as a school, raise an Unauthorized error
        if request.user.getUserType() != "school":
            return HttpResponse("You are not a school", status=UNAUTHORIZED)

        # get the data from the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:

            # serialize the data and create a new course
            course_serializer = CreateCourseSerializer(data=body_json)

            # if the data is valid, create the course and return a status code success
            if course_serializer.is_valid():
                Course.objects.create(**course_serializer.validated_data)
                return HttpResponse({"status": "success"}, status=OK)

            # if the data is not valid, return a status code bad request
            else:
                return HttpResponseBadRequest("Invalid data")

        # if the serializer raises an error, return error
        except serializers.ValidationError as e:
            return HttpResponseBadRequest(json.dumps(e.detail))

    # if method is GET, return the create course page and check if the user is a school
    user_type = request.user.getUserType()

    # if the user is a school, return the create course page, else set school to None and return the create course page
    if user_type == "school":

        # get the school from the database
        school = list(School.objects.filter(users=request.user).values())[0]

    else:
        school = None

    return render(request, "create_course.html", {"school": school})
