from __future__ import absolute_import
import requests
from authentication.models import Company
import json

from job.celery import app as celery_app


@celery_app.task
def get_api_data():
    LA_BONNE_ALTERNANCE_API_URL = 'https://labonnealternance.apprentissage.beta.gouv.fr/api/V1/jobs?romes=F1603&latitude=47.218371&longitude=-1.553621&radius=50&insee=44109&sources=&caller=contact-nantes%40ynov.com'
    response = requests.get(LA_BONNE_ALTERNANCE_API_URL)
    response_json = json.loads(response.text)

    for i in response_json['peJobs']['results']:
        print('dzadza', i)
        for j in i:
            Company.objects.update_or_create(
                name=j.company.name,
                defaults={
                    'description': j.company.description,
                    'city': j.company.headquarters.city,
                    'street': j.company.headquarters.address,
                    'zip_code': j.company.zipCode,
                }
            )

    for i in response_json['matchas']['results']:
        print('dzadza', i)
        for j in i:
            Company.objects.update_or_create(
                name=j.company.name,
                defaults={
                    'description': j.company.description,
                    'city': j.company.headquarters.city,
                    'street': j.company.headquarters.address,
                    'zip_code': j.company.zipCode,
                }
            )

    for j in response_json['lbaCompanies']['results']:
        description = getattr(j['company'], 'description', 'default')
        if hasattr(j['company'], 'headquarters'):
            city = getattr(j['company']['headquarters'], 'city', 'default')
            street = getattr(j['company']['headquarters'],
                             'address', 'default')
            zip_code = getattr(
                j['company']['headquarters'], 'zipCode', 'default')
        else:
            city = 'default'
            street = 'default'
            zip_code = 1368

        Company.objects.update_or_create(
            name=j['company']['name'],
            defaults={
                'description': description,
                'city': city,
                'street':  street,
                'zip_code':  zip_code,
            }
        )
