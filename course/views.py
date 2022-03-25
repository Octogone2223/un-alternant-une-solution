import json
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from authentication.models import Student, School, User
from .models import Course
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def list_courses(request):
    filters = {}

    location = request.GET.get('location', None)
    if location:
        if location.isnumeric():
            filters['school__zip_code'] = location
        else:
            filters['school__city'] = location

    name = request.GET.get('name', None)
    if name:
        filters['name__icontains'] = name

    school = request.GET.get('school', None)
    if school:
        filters['school__name__icontains'] = school

    courses = Course.objects.filter(**filters)[:20]
    return render(request, 'list_courses.html', {'courses': courses})


def preview_course(request, course_id):
    course = list(Course.objects.filter(id=course_id).values('id', 'name', 'description',
                  'school__name', 'school__street', 'school__city', 'school__zip_code'))[0]

    return JsonResponse({'course': course})


@login_required
def course_detail(request, course_id):
    student = Student.objects.get(user=request.user)

    if request.method == 'PATCH':
        student.course_id = course_id
        student.save()
        return JsonResponse({'status': 'success'})

    has_already_enrolled = False

    if student.course_id:
        has_already_enrolled = True

    course = Course.objects.get(id=course_id)
    return render(request, 'course_detail.html', {'course': course, 'has_already_enrolled': has_already_enrolled, 'student': student})


@login_required(login_url='authentication:sign_in')
def create_course(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        print(body)
        bodyJSON = json.loads(body)

        try:
            course = Course.objects.create(
                name=bodyJSON['name'],
                description=bodyJSON['description'],
                school_id=bodyJSON['school_id']
            )

            course.save()

            return JsonResponse({'status': 'success'})
        except Course.DoesNotExist as e:
            return HttpResponseBadRequest({'status': 'failed'})

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    if userType == 'School':
        school = list(School.objects.filter(
            users=request.user).values())[0]
    else:
        school = None

    return render(request, 'create_course.html', {'school': school})
