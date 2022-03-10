from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
import requests

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'un_alternant_une_solution_webapp.settings')
app = Celery('un_alternant_une_solution_webapp')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def get_api_data(self):
    LA_BONNE_ALTERNANCE_API_URL = 'https://labonnealternance.apprentissage.beta.gouv.fr/api/V1/formations?romes=F1603%2CI1308&latitude=48.845&longitude=2.3752&radius=30&diploma=3&caller=contact%40domaine%20nom_de_societe'
    response = requests.get(LA_BONNE_ALTERNANCE_API_URL)
    print(response.text)
