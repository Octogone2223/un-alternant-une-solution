from django.contrib import admin

from job.models import Job, JobCode, JobDating

# Register your models here.
admin.site.register(Job)
admin.site.register(JobCode)
admin.site.register(JobDating)
