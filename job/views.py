from django.shortcuts import render, redirect
from .models import Job
from authentication.models import Company
from django.http.response import HttpResponse, JsonResponse
from django.core import serializers


def list_jobs(request):
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

    jobs = Job.objects.filter(**filters)[:20]
    return render(request, 'list_jobs.html', {'jobs': jobs})


def preview_job(request, job_id):
    job = list(Job.objects.filter(id=job_id).values('id', 'name', 'description',
               'wage', 'contract_type', 'start_date', 'schedule', 'company__name', 'company__city', 'company__street', 'company__zip_code'))[0]

    return JsonResponse({'job': job})


def job_detail(request, job_id):
    job = Job.objects.get(id=job_id)
    return render(request, 'job_details.html', {'job': job})
