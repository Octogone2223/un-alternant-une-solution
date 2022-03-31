import datetime
from http.client import BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK, UNAUTHORIZED
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from rest_framework import serializers
from job.serializers import JobCreationSerializer
from .models import Job, JobDating, JobStatus
from authentication.models import Company, Student, User
from django.http.response import HttpResponse, JsonResponse
import json
from django.contrib.auth.decorators import login_required
import os
from authentication.models import User
from django.shortcuts import redirect, render
from django.http import FileResponse
from django.conf import settings
from webpush import send_user_notification


# Used to handle the fetch of all saved jobs
def list_jobs(request):
    filters = {}

    # get filters from request and add them to the filters dict
    location = request.GET.get("location", None)
    if location:
        if location.isnumeric():
            filters["company__zip_code"] = location
        else:
            filters["company__city"] = location

    profession = request.GET.get("profession", None)
    if profession:
        filters["name__icontains"] = profession

    contact_type = request.GET.get("contact_type", None)
    if contact_type:
        filters["contract_type__icontains"] = contact_type

    # get jobs from database with filters, only 20 jobs at a time
    jobs = Job.objects.filter(**filters)[:20]

    # return list of jobs page with jobs
    return render(request, "list_jobs.html", {"jobs": jobs})


# Used to handle the creation of a new job for a specific user (must be logged in as a company)
@login_required
def create_job(request):

    # if user wants to create a job
    if request.method == "POST":

        # if not logged in as a company raise unauthorized
        if request.user.getUserType() != "Company":
            return HttpResponse("You are not a school", status=UNAUTHORIZED)

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:

            # serialize the job
            jobCreationSerializer = JobCreationSerializer(data=body_json)

            # if serialization is valid save the job and return the job as http response
            if jobCreationSerializer.is_valid():

                company = Company.objects.filter(
                    users__pk=request.user.id).first()
                job = Job.objects.create(
                    **jobCreationSerializer.validated_data)
                job.company = company
                job.save()

                return JsonResponse({"status": "success"})

            # if serialization is not valid return the errors as http response
            else:
                return HttpResponseBadRequest("Invalid data")

        # if something goes wrong on the validation return the errors as http response
        except serializers.ValidationError as e:
            return HttpResponseBadRequest(json.dumps(e.detail))

    # if user wants to see the create job page
    user_json = list(User.objects.filter(id=request.user.id).values())[0]
    user_type = request.user.getUserType()

    # if user is logged in as a company
    if user_type == "Company":

        # get the company
        company = list(Company.objects.filter(users=request.user).values())[0]

        # return the create job page with company, user and user_type as context
        return render(
            request,
            "create_job.html",
            {"user": user_json, "userType": user_type, "company": company},
        )

    # if user is not logged in as a company redirect to profile page
    else:
        return redirect("/profile")


# Used to handle the update of a job for a specific user (must be logged in as a company)
@login_required
def update_job(request, job_id):

    # if user wants to update a job
    if request.method == "PUT":

        # if not logged in as a company raise unauthorized
        if request.user.getUserType() != "Company":
            return HttpResponse("You are not a school", status=UNAUTHORIZED)

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:

            # serialize the job
            job_update_serializer = JobCreationSerializer(data=body_json)

            # if serialization is valid save the job and return the job as http response
            if job_update_serializer.is_valid():

                # get the job from the database and update it with the new data
                job = Job.objects.get(id=job_id).update(
                    **job_update_serializer.validated_data
                )
                job.save()

                # return an success message
                return JsonResponse({"status": "success"})

            # if serialization is not valid return the errors as http response
            else:
                return HttpResponseBadRequest("Invalid data")

        # if job does not exist return an error
        except Job.DoesNotExist:
            return HttpResponseBadRequest({"status": "failed"})

    # if user wants to see the update job page
    try:

        # get the job from the database
        company = list(Company.objects.filter(users=request.user).values())[0]
        job = list(
            Job.objects.filter(id=job_id, company_id=company["id"]).values(
                "id",
                "name",
                "description",
                "wage",
                "contract_type",
                "start_date",
                "schedule",
                "company_id",
            )
        )[0]

        # return the update job page with job, company and job as context
        return render(request, "update_job.html", {"job": job, "company": company})

    # if job does not exist return an error
    except Job.DoesNotExist:
        return HttpResponseBadRequest("Job does not exist")


# Used to fetch the details of a specific job (api)
def preview_job(request, job_id):

    try:

        # get the job from the database and return it as http response
        job = list(
            Job.objects.filter(id=job_id).values(
                "id",
                "name",
                "description",
                "wage",
                "contract_type",
                "start_date",
                "schedule",
                "company__name",
                "company__city",
                "company__street",
                "company__zip_code",
            )
        )[0]

        return JsonResponse({"job": job})

    # if job does not exist return an error
    except Job.DoesNotExist:
        return HttpResponseBadRequest("Job does not exist")


# method to handle the upload of a file (cv and motivation letter)
def handle_uploaded_file(f, type):

    # generate a unique filename for the file with the current time
    file_name_with_timeseconds = (
        f.name + str(datetime.datetime.now().timestamp()) + ".pdf"
    )

    # save the file at the uploads folder (type)
    with open(f"core/files/{type}/{file_name_with_timeseconds}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # return the path of the file
    return f"core/files/{type}/{file_name_with_timeseconds}"


# Used to handle the deletion of a file
def handle_delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


# job detail view (must be logged in)
@login_required
def job_detail(request, job_id):

    # if company wants to delete one of its jobs
    if request.method == "DELETE":

        # if not logged in as a company redirect to home page
        company = Company.objects.filter(users__pk=request.user.id).first()
        if company is None:
            return redirect("/")

        try:

            # get the job from the database and delete it
            Job.objects.get(company=company, id=job_id).delete()

            # return an success status
            return HttpResponse(status=OK)

        # if job does not exist return an error
        except Job.DoesNotExist:
            return HttpResponse(status=NOT_FOUND)

    # if user wants to see the job detail page
    # by default the user is a student and doesn't have applied to this actual job
    has_already_applied = False
    is_user = True

    # if it is not a student set is_user to false
    if request.user.getUserType() != "Student":
        is_user = False

    # if the user is logged in as a student
    else:

        # search if the user has already applied to this job and set has_already_applied to true if it has
        has_already_applied = JobDating.objects.filter(
            job_id=job_id, student=request.user.student
        ).exists()

    # if the student wants to apply to a job and he has not already applied to it
    if request.method == "POST" and not has_already_applied:

        # get the cv and motivation letter from the request
        cv = request.FILES.get("cv", None)
        motivation_letter = request.FILES.get("motivation_letter", None)

        # if the cv or the motivation letter is not attached to the request return an error
        if not cv or not motivation_letter:
            return HttpResponse(status=BAD_REQUEST)

        # call the handle_uploaded_file method to save the files
        cv_path = handle_uploaded_file(cv, "cv")
        motivation_letter_path = handle_uploaded_file(
            motivation_letter, "motivation_letter"
        )

        # create a new job dating object (doesn't need to be check by serializer because we set the fields manually)
        job_dating = JobDating.objects.create(
            cv_path=cv_path,
            motivation_letter_path=motivation_letter_path,
            job_id=job_id,
            student=request.user.student,
            status=JobStatus.Status.OPEN,
        )

        job_dating.save()

        # get the actual job from the database and add the job dating to the job
        job = Job.objects.filter(id=job_id).first()
        job.job_datings.add(job_dating)

        # return an success status
        return HttpResponse(status=CREATED)

    # if the user wants to see the job detail page
    job = Job.objects.get(id=job_id)

    # return the job detail page with job, has_already_applied and is_user as context
    return render(
        request,
        "job_details.html",
        {"job": job, "has_already_applied": has_already_applied, "is_user": is_user},
    )


# Used to retrieve the list of all job applications for a specific company (must be logged in)
@login_required
def jobs_datings(request):

    # if the user is a student
    if hasattr(request.user, "student"):

        # get all jobs datings for the student and return the jobs datings page with jobs datings as context
        job_datings = JobDating.objects.filter(student=request.user.student)
        return render(
            request, "jobs_datings_student.html", {"job_datings": job_datings}
        )

    # if it is not a student
    else:
        try:

            # get the user company
            company = Company.objects.filter(users__pk=request.user.id).first()

            # if it a school redirect to home page
            if company is None:
                return redirect("/")

            # get all jobs for the company and return the jobs datings page with jobs as context
            jobs = Job.objects.filter(company=company)
            return render(request, "jobs_datings_company.html", {"jobs": jobs})

        # if company does not exist redirect to home page
        except Company.DoesNotExist:
            return redirect("/")


# Used to handle job applications (must be logged in)
@login_required
def jobs_datings_detail(request, job_dating_id):

    # if the company wants to update the status of a job dating (reject or accept)
    if request.method == "PATCH":

        # if not logged in as a company redirect to home page
        company = Company.objects.filter(users__pk=request.user.id).first()
        if company is None:
            return redirect("/")

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:
            # create a payload for the webhook
            payload = {"head": "", "body": "", "url": "/jobs/datings"}

            # get the job dating from the database associated to the user company
            job_dating = JobDating.objects.get(
                id=job_dating_id, job__company__users=request.user
            )

            # if the status is accept
            if body_json["status"] == "ACCEPTED":

                # set the status of the job dating to ACCEPTED
                job_dating.status = "AC"

                # set the payload head and body
                payload["head"] = "Candidature Acceptée !"
                payload[
                    "body"
                ] = f"Votre candidature pour '${job_dating.job.name}' a été acceptée 😁!"

            # if the status is reject
            elif body_json["status"] == "REJECTED":

                # set the status of the job dating to REJECTED
                job_dating.status = "RE"

                # set the payload head and body
                payload["head"] = "Candidature Rejetée !"
                payload[
                    "body"
                ] = f"Votre candidature pour '${job_dating.job.name}' a été rejetée 😖!"

            # pass the webhook payload to the webhook and send a notification to the student
            send_user_notification(
                user=job_dating.student.user, payload=payload, ttl=1000
            )

            # save the job dating
            job_dating.save()

            # return an success status
            return HttpResponse(status=OK)

        # if job dating does not exist return an error
        except JobDating.DoesNotExist:
            return HttpResponse(status=NOT_FOUND)

    # if the student wants to delete his job dating
    if request.method == "DELETE":

        # if not logged in as a student redirect to home page
        student = Student.objects.filter(user=request.user).first()
        if student is None:
            return redirect("/")

        # get the job dating from the database and delete it
        job_dating = JobDating.objects.get(id=job_dating_id, student=student)
        job_dating.delete()

        # call the delete_file method to delete the files
        handle_delete_file(job_dating.cv_path)
        handle_delete_file(job_dating.motivation_letter_path)

        # return an success status
        return HttpResponse(status=NO_CONTENT)


# Used to retrieve details of a specific job application (must be logged in)
@login_required
def job_inspect(request, job_id):
    try:

        # if the user is not a company redirect to home page
        if request.user.getUserType() != "Company":
            return redirect("/")

        # get the job from the database associated to the user company and all the job datings associated to the job
        job = Job.objects.get(id=job_id, company__users__pk=request.user.id)
        job_datings = job.job_datings.all()

        # return the job inspect page with job and job datings as context
        return render(
            request, "job_inspect.html", {
                "job": job, "job_datings": job_datings}
        )

    # if job does not exist return an error
    except Job.DoesNotExist:
        return redirect("/")


# if the company wants to inspect the cv of a student who applied to a job (must be logged in)
@login_required
def job_dating_inspect_cv(request, job_dating_id):
    try:

        # if the user is not a company redirect to home page
        if request.user.getUserType() != "Company":
            return redirect("/")

        # get the job dating from the database associated to the user company
        job_dating = JobDating.objects.get(
            id=job_dating_id, job__company__users=request.user
        )

        # return the cv of the job dating
        return FileResponse(open(f"{settings.BASE_DIR}/{job_dating.cv_path}", "rb"))

    # if job dating does not exist redirect to home page
    except JobDating.DoesNotExist:
        return redirect("/")


# if the company wants to inspect the motivation letter of a student who applied to a job (must be logged in)
@login_required
def job_dating_inspect_letter(request, job_dating_id):
    try:

        # if the user is not a company redirect to home page
        if request.user.getUserType() != "Company":
            return redirect("/")

        # get the job dating from the database associated to the user company
        job_dating = JobDating.objects.get(
            id=job_dating_id, job__company__users=request.user
        )

        # return the motivation letter of the job dating
        return FileResponse(
            open(f"{settings.BASE_DIR}/{job_dating.motivation_letter_path}", "rb")
        )

    # if job dating does not exist redirect to home page
    except JobDating.DoesNotExist:
        return redirect("/")
