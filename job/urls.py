from django.urls import path
from . import views

urlpatterns = [
    # list of jobs
    path("", views.list_jobs, name="list_jobs"),
    # job detail
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    # update a job
    path("update/<int:job_id>/", views.update_job, name="update_job"),
    # inspect all jobs datings (company only)
    path("<int:job_id>/inspect", views.job_inspect, name="job_inspect"),
    # preview of a job (api)
    path("preview/<int:job_id>/", views.preview_job, name="preview_job"),
    # create a job (company only)
    path("create-job/", views.create_job, name="create_job"),
    # job datings page
    path("datings/", views.jobs_datings, name="jobs_datings"),
    # job datings details (company only)
    path(
        "datings/<int:job_dating_id>",
        views.jobs_datings_detail,
        name="jobs_datings_detail",
    ),
    # job datings inspect cv (company only)
    path(
        "datings/<int:job_dating_id>/inspect-cv",
        views.job_dating_inspect_cv,
        name="job_dating_inspect_cv",
    ),
    # job datings inspect motivation letter (company only)
    path(
        "datings/<int:job_dating_id>/inspect-letter",
        views.job_dating_inspect_letter,
        name="job_dating_inspect_letter",
    ),
]
