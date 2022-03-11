from django.db import models

# Create your models here.


class JobCode (models.Model):
    class Meta:
        db_table = "job_code"

    name = models.CharField(max_length=255)
    code = models.IntegerField()

    def __str__(self):
        return self.name
