from __future__ import absolute_import
import datetime
from time import time
import requests
from authentication.models import Company
import json

from job.celery import app as celery_app
from job.models import Job, JobCode, LastIndexApi


@celery_app.task
def get_api_data():
    last_index_api, created = LastIndexApi.objects.get_or_create(
        pk=1, defaults={'last_index': 0})

    job_codes = JobCode.objects.all().order_by(
        'id').filter(pk__gt=last_index_api.last_index)[:9]

    if job_codes.count() == 0:
        job_codes = JobCode.objects.all().order_by(
            'id').filter(pk__gt=0)[:9]

    job_codes_comma = ','.join(str(job_code.code) for job_code in job_codes)

    LA_BONNE_ALTERNANCE_API_URL = f'https://labonnealternance.apprentissage.beta.gouv.fr/api/V1/jobs?romes={job_codes_comma}&latitude=47.218371&longitude=-1.553621&radius=50&insee=44109&sources=offres,matcha&caller=contact%40domaine%20nom_de_societe'
    response = requests.get(LA_BONNE_ALTERNANCE_API_URL)

    if response.status_code != 200:
        return

    if job_codes.count() != 0:
        LastIndexApi.objects.filter(pk=1).update(
            last_index=last_index_api.last_index + 9)
    else:
        LastIndexApi.objects.filter(pk=1).update(
            last_index=9)

    response_json = json.loads(response.text)

    for result in response_json['peJobs']['results']:
        company = createCompany(result['company'])

        if company is not None:
            createJob(result, company)

    for result in response_json['matchas']['results']:
        company = createCompany(result['company'])

        if company is not None:
            createJob(result, company)


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
                'street':  street,
                'zip_code':  zip_code,
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
