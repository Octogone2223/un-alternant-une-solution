from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Job(models.Model):
    class Meta:
        db_table = "job"

    class ContractType(models.TextChoices):
        ALTERNANCE = 'AL', _('Alternance')
        INTERNSHIP = 'IN', _('Internship')
        FULL_TIME = 'FT', _('Full Time')
        PART_TIME = 'PT', _('Part Time')
        CONTRACT = 'CT', _('Contract')
        VOLUNTEER = 'VO', _('Volunteer')
        OTHER = 'OT', _('Other')

    name = models.CharField(max_length=255)
    description = models.TextField()
    wage = models.FloatField()
    contract_type = models.CharField(
        max_length=2,
        choices=ContractType.choices,
    )
    start_date = models.DateField()
    schedule = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

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
