from django.shortcuts import render, redirect
from .models import Job
from authentication.models import Company
from django.http.response import HttpResponse, JsonResponse
from django.core import serializers


def list_jobs(request):
    jobs = Job.objects.all()[:10]
    return render(request, 'list_jobs.html', {'jobs': jobs})


def job_detail(request, job_id):
    job = list(Job.objects.filter(id=job_id).values())[0]
    return JsonResponse({'job': job})
