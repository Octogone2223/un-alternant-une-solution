from django.db import models
from authentication.models import Company, Student, UserManager
from job.models import Job

# Create your models here.


class Status(models.Model):
    class Meta:
        db_table = "status"

    name = models.CharField(max_length=75, verbose_name="Profession Name")

    def __str__(self):
        return f'{self.name}'


class JobDating(models.Model):
    class Meta:
        db_table = "jobDating"

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    motivation_letter_path = models.CharField(
        max_length=255, verbose_name="Job Name")
    cv_path = models.CharField(max_length=255, verbose_name="Job Name")
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student.firstname | self.job.name}'


class Profession(models.Model):
    class Meta:
        db_table = "profession"

    name = models.CharField(max_length=75, verbose_name="Profession Name")
    code = models.IntegerField(verbose_name="Profession Code")

    def __str__(self):
        return f'{self.name} | {self.code}'


class Course(models.Model):
    class Meta:
        db_table = "course"

    name = models.CharField(max_length=75, verbose_name="Course Name")
    description = models.TextField(verbose_name="Course Description")
    listProfessions = models.ManyToManyField(Profession)

    def __str__(self):
        return f'{self.name}'
