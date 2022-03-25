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
import os
from authentication.models import User
from django.shortcuts import render, redirect, reverse
from django.db.models import Prefetch
from django.http import FileResponse
from django.conf import settings
from webpush import send_user_notification


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
        except Exception as e:
            print(e)
            return HttpResponseBadRequest({'status': 'failed'})

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    if userType == 'Company':
        company = list(Company.objects.filter(
            users=request.user).values())[0]
        return render(request, 'create_job.html', {'user': userJSON, 'userType': userType, 'company': company})
    else:
        return redirect('/profile')


@login_required(login_url='authentication:sign_in')
def update_job(request, job_id):

    if request.method == 'PUT':
        body = request.body.decode('utf-8')
        print(body)
        bodyJSON = json.loads(body)
        print(bodyJSON)
        try:
            job = Job.objects.get(id=job_id)

            job.name = bodyJSON['name']
            job.description = bodyJSON['description']
            job.wage = bodyJSON['wage']
            job.contract_type = bodyJSON['contract_type']
            job.start_date = bodyJSON['start_date']
            job.schedule = bodyJSON['schedule']
            job.company_id = bodyJSON['company_id']

            job.save()
            return JsonResponse({'status': 'success'})
        except Job.DoesNotExist:
            return HttpResponseBadRequest({'status': 'failed'})

    try:
        company = list(Company.objects.filter(
            users=request.user).values())[0]
        job = list(Job.objects.filter(id=job_id, company_id=company['id']).values('id', 'name', 'description',
                                                                                  'wage', 'contract_type', 'start_date', 'schedule', 'company_id'))[0]

        return render(request, 'update_job.html', {'job': job, 'company': company})
    except Job.DoesNotExist:
        return HttpResponseBadRequest()


def preview_job(request, job_id):
    job = list(Job.objects.filter(id=job_id).values('id', 'name', 'description',
               'wage', 'contract_type', 'start_date', 'schedule', 'company__name', 'company__city', 'company__street', 'company__zip_code'))[0]

    return JsonResponse({'job': job})


def handle_uploaded_file(f, type):
    file_name_with_timeseconds = f.name + \
        str(datetime.datetime.now().timestamp()) + '.pdf'

    with open(f'core/files/{type}/{file_name_with_timeseconds}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return f'core/files/{type}/{file_name_with_timeseconds}'


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
        except Job.DoesNotExist:
            return HttpResponse(status=400)

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

        job = Job.objects.filter(id=job_id).first()
        job.job_datings.add(job_dating)

        return HttpResponse(status=201)

    job = Job.objects.get(id=job_id)

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
    if request.method == 'PATCH':
        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        try:
            payload = {"head": "", "body": "","url": "/jobs/datings"}
            job_dating = JobDating.objects.get(
                id=job_dating_id, job__company__users=request.user)
            if bodyJson['status'] == 'ACCEPTED':
                job_dating.status = 'AC'
                payload['head'] = "Candidature Accepté !"
                payload['body'] = f"Votre candidature pour '${job_dating.job.name}' a été accepté 😁!"
            elif bodyJson['status'] == 'REJECTED':
                job_dating.status = 'RE'
                payload['head'] = "Candidature Rejeté !"
                payload['body'] = f"Votre candidature pour '${job_dating.job.name}' a été rejeté 😖!"


            send_user_notification(user=job_dating.student.user, payload=payload, ttl=1000)

            job_dating.save()
            return HttpResponse(status=200)

        except JobDating.DoesNotExist:
            return HttpResponse(status=400)

    if request.method == 'DELETE':
        job_dating = JobDating.objects.get(id=job_dating_id)
        job_dating.delete()

        handle_delete_file(job_dating.cv_path)
        handle_delete_file(job_dating.motivation_letter_path)

        return HttpResponse(status=204)


@ login_required
def job_inspect(request, job_id):
    try:
        job = Job.objects.get(id=job_id, company__users__pk=request.user.id)
        job_datings = job.job_datings.all()
        return render(request, 'job_inspect.html', {'job': job, 'job_datings': job_datings})
    except Job.DoesNotExist:
        return redirect('/')


@ login_required
def job_dating_inspect_cv(request, job_dating_id):
    try:
        job_dating = JobDating.objects.get(
            id=job_dating_id, job__company__users=request.user)
        return FileResponse(open(f'{settings.BASE_DIR}/{job_dating.cv_path}', "rb"))
    except JobDating.DoesNotExist:
        return redirect('/')


@ login_required
def job_dating_inspect_letter(request, job_dating_id):
    try:
        job_dating = JobDating.objects.get(
            id=job_dating_id, job__company__users=request.user)
        return FileResponse(open(f'{settings.BASE_DIR}/{job_dating.motivation_letter_path}', "rb"))
    except JobDating.DoesNotExist:
        return redirect('/')
