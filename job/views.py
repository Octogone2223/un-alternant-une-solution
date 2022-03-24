import datetime
from django.shortcuts import render, redirect
from .models import Job, JobDating, JobStatus
from authentication.models import Company
from django.http.response import HttpResponse, JsonResponse
from django.core import serializers
import json
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .serializers import JobDatingSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
import os
from authentication.models import User
from django.shortcuts import render, redirect, reverse
from django.db.models import Prefetch


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


def handle_uploaded_file(f, type):
    file_name_with_timeseconds = f.name + \
        str(datetime.datetime.now().timestamp()) + '.pdf'

    with open(f'app/files/{type}/{file_name_with_timeseconds}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return f'app/files/{type}/{file_name_with_timeseconds}'


def handle_delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


@login_required
def job_detail(request, job_id):
    if request.method == 'DELETE':
        company = Company.objects.filter(users__pk=request.user.id).first()
        if company is None:
            return redirect('/')

        try:
            Job.objects.get(
                company=company, id=job_id).delete()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=400)

    if(not hasattr(request.user, 'student')):
        not_user = True

    else:
        has_already_applied = JobDating.objects.filter(
            job_id=job_id, student=request.user.student).exists()

    if request.method == 'POST' and not has_already_applied and not_user:
        cv = request.FILES.get('cv', None)
        motivation_letter = request.FILES.get('motivation_letter', None)

        if not cv or not motivation_letter:
            return HttpResponse(status=400)

        cv_path = handle_uploaded_file(cv, 'cv')
        motivation_letter_path = handle_uploaded_file(
            motivation_letter, 'motivation_letter')

        job_dating = JobDating(cv_path=cv_path, motivation_letter_path=motivation_letter_path,
                               job_id=job_id, student=request.user.student, status=JobStatus.Status.OPEN)

        job_dating.save()

        job = Job.objects.filter(id=job_id).first()
        job.job_datings.add(job_dating)

        return HttpResponse(status=201)

    job = Job.objects.get(id=job_id)

    if not_user:
        return render(request, 'job_details.html', {'job': job, 'not_user': not_user, 'has_already_applied': True})

    return render(request, 'job_details.html', {'job': job, 'has_already_applied': has_already_applied})


@ login_required
def jobs_datings(request):

    if hasattr(request.user, 'student'):
        job_datings = JobDating.objects.filter(student=request.user.student)
        return render(request, 'jobs_datings_student.html', {'job_datings': job_datings})

    else:
        try:
            company = Company.objects.filter(users__pk=request.user.id).first()
            if company is None:
                return redirect('/')

            jobs = Job.objects.filter(
                company=company)

            return render(request, 'jobs_datings_company.html', {'jobs': jobs})
        except Company.DoesNotExist:
            return redirect('/')


@ login_required
def jobs_datings_detail(request, job_dating_id):
    if request.method == 'DELETE':
        job_dating = JobDating.objects.get(id=job_dating_id)
        job_dating.delete()

        handle_delete_file(job_dating.cv_path)
        handle_delete_file(job_dating.motivation_letter_path)

        return HttpResponse(status=204)
