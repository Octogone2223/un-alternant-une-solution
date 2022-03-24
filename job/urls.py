from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_jobs, name='list_jobs'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/inspect', views.job_inspect, name='job_inspect'),
    path('preview/<int:job_id>/', views.preview_job, name='preview_job'),
    path('create-job/', views.create_job, name="create_job"),
    path('datings/', views.jobs_datings, name='jobs_datings'),
    path('datings/<int:job_dating_id>', views.jobs_datings_detail,
         name='jobs_datings_detail'),
    path("datings/<int:job_dating_id>/inspect-cv",
         views.job_dating_inspect_cv, name="job_dating_inspect_cv"),
    path("datings/<int:job_dating_id>/inspect-letter",
         views.job_dating_inspect_letter, name="job_dating_inspect_letter")
]
