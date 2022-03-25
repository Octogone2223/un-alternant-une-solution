from django.shortcuts import render

from authentication.models import Student, User
from .models import Course
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def list_courses(request):
    filters = {}

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

    courses = Course.objects.filter(**filters)[:20]
    return render(request, "list_courses.html", {"courses": courses})


def preview_course(request, course_id):
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

    return JsonResponse({"course": course})


@login_required
def course_detail(request, course_id):
    student = None

    if request.user.getUserType == "student":
        student = Student.objects.get(user=request.user)

    if request.method == "PATCH":
        student.course_id = course_id
        student.save()
        return JsonResponse({"status": "success"})

    has_already_enrolled = False

    if student and student.course_id:
        has_already_enrolled = True

    course = Course.objects.get(id=course_id)
    return render(
        request,
        "course_detail.html",
        {
            "course": course,
            "has_already_enrolled": has_already_enrolled,
            "student": student,
        },
    )
