from __future__ import absolute_import
from ctypes import Array
import datetime
from time import time
import requests
from authentication.models import Company
import json

from job.celery import app as celery_app
from job.models import Job, JobCode, JobIdFromPreviousRequest, LastIndexApi


@celery_app.task
def get_api_data():
    last_index_api, created = LastIndexApi.objects.get_or_create(
        pk=1, defaults={'pk': 1, 'last_index': 0})

    print(last_index_api)

    job_codes = JobCode.objects.all().order_by(
        'code', 'id').distinct('code').filter(pk__gt=last_index_api.last_index)[:9]

    if job_codes.count() == 0:
        job_codes = JobCode.objects.all().order_by(
            'id').filter(pk__gt=0)[:9]

        LastIndexApi.objects.filter(pk=1).update(
            last_index=0)
    else:
        LastIndexApi.objects.filter(pk=1).update(
            last_index=list(job_codes.values_list('id', flat=True))[-1])

    job_codes_comma = ','.join(str(job_code.code) for job_code in job_codes)

    LA_BONNE_ALTERNANCE_API_URL = f'https://labonnealternance.apprentissage.beta.gouv.fr/api/V1/jobs?romes={job_codes_comma}&latitude=47.218371&longitude=-1.553621&radius=50&insee=44109&sources=offres,matcha&caller=contact%40domaine%20nom_de_societe'
    response = requests.get(LA_BONNE_ALTERNANCE_API_URL)

    if response.status_code != 200:
        return

    response_json = json.loads(response.text)
    listJobIdFromResponse = []

    for result in response_json['peJobs']['results']:
        company = createCompany(result['company'])
        listJobIdFromResponse.append(result['job']['id'])

        if company is not None:
            createJob(result, company)

    for result in response_json['matchas']['results']:
        company = createCompany(result['company'])
        listJobIdFromResponse.append(result['job']['id'])

        if company is not None:
            createJob(result, company)

    print(listJobIdFromResponse)
    jobs_codes_request = list(map(lambda x: x.code, job_codes))

    deleteOldJobs(listJobIdFromResponse, jobs_codes_request)

    JobIdFromPreviousRequest.objects.create(
        job_ids=listJobIdFromResponse,
        job_codes=jobs_codes_request
    )


def createCompany(company):
    if "description" in company:
        description = company['description']
    else:
        description = None
    if getattr(company, 'headquarter', None) is not None:
        street = company['headquarter']['address']
        city = company['headquarter']['city']
        zip_code = company['zipCode']
    else:
        street = None
        city = None
        zip_code = None

    if "name" in company:
        company, created = Company.objects.update_or_create(
            name=company['name'],
            defaults={
                'description': description,
                'city': city,
                'street': street,
                'zip_code': zip_code,
            }
        )
        return company


def createJob(request, company):

    if "title" in request:
        title = request['title']
    else:
        title = None

    if "description" in request['job']:
        description = request['job']['description']
    else:
        description = None

    if 'contractType' in request['job']:
        contract_type = request['job']['contractType']
    else:
        contract_type = None

    if 'jobStartDate' in request['job']:
        start_date = request['job']['jobStartDate']
    else:
        start_date = datetime.datetime.now()

    if 'duration' in request['job']:
        schedule = request['job']['duration']
    else:
        schedule = None

    if title and description and contract_type and start_date and schedule:
        job, created = Job.objects.update_or_create(
            api_id=request['job']['id'],
            defaults={
                'name': title,
                'description': description,
                'contract_type': contract_type,
                'start_date': start_date,
                'schedule': schedule,
            }
        )
        company.jobs.add(job)
        return job


def deleteOldJobs(listJobIdFromResponse, jobs_codes_request):
    old_jobs = JobIdFromPreviousRequest.objects.filter(
        job_codes__contains=jobs_codes_request)

    for old_job in old_jobs:
        for old_job_id in old_job.job_ids:
            if old_job_id not in listJobIdFromResponse:
                print(f'Delete job {old_job_id}')
                job = Job.objects.get(api_id=old_job_id)
                job.delete()
                old_job.delete()
