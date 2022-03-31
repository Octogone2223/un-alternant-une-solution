from django.contrib import admin
from .models import Company, School, Student, User

# Register your models here.
admin.site.register(User)
admin.site.register(Company)
admin.site.register(School)
admin.site.register(Student)
