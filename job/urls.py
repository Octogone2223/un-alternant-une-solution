from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_jobs, name='list_jobs'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('preview/<int:job_id>/', views.preview_job, name='preview_job'),
    path('datings/', views.jobs_datings, name='jobs_datings'),
    path('datings/<int:job_dating_id>', views.jobs_datings_detail,
         name='jobs_datings_detail')
]
