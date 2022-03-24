from django.shortcuts import render
from .models import Course
from django.http.response import HttpResponse, JsonResponse

# Create your views here.


def list_courses(request):
    filters = {}

    location = request.GET.get('location', None)
    if location:
        if location.isnumeric():
            filters['company__zip_code'] = location
        else:
            filters['company__city'] = location

    profession = request.GET.get('profession', None)
    if profession:
        filters['name__icontains'] = profession

    contact_type = request.GET.get('contact_type', None)
    if contact_type:
        filters['contract_type__icontains'] = contact_type

    courses = Course.objects.filter(**filters)[:20]
    return render(request, 'list_courses.html', {'courses': courses})


def preview_course(request, course_id):
    course = list(Course.objects.filter(id=course_id).values('id', 'name', 'description',
                  'school__name', 'school__street', 'school__city', 'school__zip_code'))[0]

    return JsonResponse({'course': course})


def course_detail(request, course_id):
    return render(request, 'course_detail.html')
