from __future__ import absolute_import
import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "un_alternant_une_solution_webapp.settings"
)

app = Celery("job")

CELERY_TIMEZONE = "UTC"

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
