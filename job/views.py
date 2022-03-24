import datetime
from distutils.log import error
from django.forms import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from .models import Job, JobDating, JobStatus
from authentication.models import Company, User
from django.http.response import HttpResponse, JsonResponse
from django.core import serializers
import json
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .serializers import JobCreationSerializer, JobDatingSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required


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


@login_required(login_url='authentication:sign_in')
def create_job(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        bodyJSON = json.loads(body)
        try:
            job = Job.objects.create(
                name=bodyJSON['name'],
                description=bodyJSON['description'],
                wage=bodyJSON['wage'],
                contract_type=bodyJSON['contract_type'],
                start_date=bodyJSON['start_date'],
                schedule=bodyJSON['schedule'],
                company_id=bodyJSON['company_id']
            )

            job.save()

            return JsonResponse({'status': 'success'})
        except:
            return HttpResponseBadRequest({'status': 'failed'})

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    if userType == 'Company':
        company = list(Company.objects.filter(
            user_companies=request.user).values())[0]
        return render(request, 'create_job.html', {'user': userJSON, 'userType': userType, 'company': company})
    else:
        return redirect('/profile')


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


@login_required
def job_detail(request, job_id):
    has_already_applied = JobDating.objects.filter(
        job_id=job_id, student=request.user.student).exists()

    if request.method == 'POST' and not has_already_applied:
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

        return HttpResponse(status=201)

    job = Job.objects.get(id=job_id)
    return render(request, 'job_details.html', {'job': job, 'has_already_applied': has_already_applied})
