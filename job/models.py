from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

# Creates a JobCode model


class JobCode(models.Model):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# Creates a Job model


class Job(models.Model):

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

    # RELATIONS
    job_datings = models.ManyToManyField("job.JobDating", related_name="job_datings+")
    company = models.ForeignKey(
        "authentication.company", on_delete=models.CASCADE, related_name="job_company+"
    )

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Creates a JobStatus model
class JobStatus(models.Model):
    class Status(models.TextChoices):
        OPEN = "OP", _("Open")
        CLOSED = "CL", _("Closed")
        CANCELED = "CA", _("Canceled")

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )

    # RELATIONS
    job = models.ForeignKey("Job", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Creates a LastIndexApi model
class LastIndexApi(models.Model):
    last_index = models.IntegerField()
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.last_index


# Creates a JobIdFromPreviousRequest model
class JobIdFromPreviousRequest(models.Model):

    # RELATIONS
    job_codes = ArrayField(base_field=models.CharField(max_length=255))
    job_ids = ArrayField(base_field=models.CharField(max_length=255))

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_id


# Creates a JobDating model
class JobDating(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "AC", _("ACCEPTED")
        REJECTED = "RE", _("REJECTED")
        PENDING = "PE", _("PENDING")

    motivation_letter_path = models.CharField(max_length=255, verbose_name="Job Name")
    cv_path = models.CharField(max_length=255, verbose_name="Job Name")
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )

    # RELATIONS
    student = models.ForeignKey("authentication.Student", on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job.name}"
