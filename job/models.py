from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from authentication.models import Company
# Create your models here.


class JobCode (models.Model):
    class Meta:
        db_table = "job_code"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Job(models.Model):
    class Meta:
        db_table = "job"

    name = models.CharField(max_length=255)
    description = models.TextField()
    wage = models.FloatField(
        null=True,
    )
    contract_type = models.CharField(max_length=100)
    start_date = models.DateField()
    schedule = models.CharField(max_length=255)
    api_id = models.CharField(max_length=255, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='job_company+')

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


class JobStatus(models.Model):
    class Meta:
        db_table = "job_status"

    class Status(models.TextChoices):
        OPEN = 'OP', _('Open')
        CLOSED = 'CL', _('Closed')
        CANCELED = 'CA', _('Canceled')

    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )

    def __str__(self):
        return self.name


class LastIndexApi(models.Model):
    class Meta:
        db_table = "last_index_api"

    last_index = models.IntegerField()

    def __str__(self):
        return self.last_index


class JobIdFromPreviousRequest(models.Model):
    class Meta:
        db_table = "job_id_from_previous_request"

    job_codes = ArrayField(base_field=models.CharField(max_length=255))
    job_ids = ArrayField(base_field=models.CharField(max_length=255))

    def __str__(self):
        return self.job_id
