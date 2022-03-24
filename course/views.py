from django.shortcuts import render
from .models import Course

# Create your views here.


def list_courses(request):
    courses = Course.objects.all()
    return render(request, 'list_courses.html', {'courses': courses})


def course_detail(request, course_id):
    return render(request, 'course_detail.html')
