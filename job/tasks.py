from __future__ import absolute_import
import datetime
import requests
from authentication.models import Company
import json
from job.celery import app as celery_app
from job.models import Job, JobCode, JobIdFromPreviousRequest, LastIndexApi


# get all jobs from api
@celery_app.task
def get_api_data():
    # get last index from database (use to know where to start) or create it if it doesn't exist yet and set it to 0
    # created is a boolean that tells if the object was created or not (but it's not used)
    last_index_api, created = LastIndexApi.objects.get_or_create(
        pk=1, defaults={"last_index": 0, "pk": 1}
    )

    # get distinct job codes from database, based on last index from database
    # we only want to get the 9 last job codes because the API only accepts 9 job codes at a time (max)
    job_codes = (
        JobCode.objects.all()
        .order_by("code", "id")
        .distinct("code")
        .filter(pk__gt=last_index_api.last_index)[:9]
    )

    # if the job_codes list is empty it means that we have already fetched all the jobs from the API
    # so we reset the last_index to 0 to refetch all the jobs from the API
    if job_codes.count() == 0:
        job_codes = JobCode.objects.all().order_by("id").filter(pk__gt=0)[:9]
        LastIndexApi.objects.filter(pk=1).update(last_index=0)

    # else we update the last_index to the last job code id get
    else:
        LastIndexApi.objects.filter(pk=1).update(
            last_index=list(job_codes.values_list("id", flat=True))[-1]
        )

    # map job codes to a list of strings (use for the request to API)
    job_codes_comma = ",".join(str(job_code.code) for job_code in job_codes)

    # URL API
    LA_BONNE_ALTERNANCE_API_URL = f"https://labonnealternance.apprentissage.beta.gouv.fr/api/V1/jobs?romes={job_codes_comma}&latitude=47.218371&longitude=-1.553621&radius=50&insee=44109&sources=offres,matcha&caller=contact%40domaine%20nom_de_societe"

    # get data from API
    response = requests.get(LA_BONNE_ALTERNANCE_API_URL)

    # if the response is not 200, we return nothing (access limited to API)
    if response.status_code != 200:
        return

    # get the body of the response
    response_json = json.loads(response.text)
    list_job_id_from_response = []

    # for each job in the peJobs attribute in the response
    for result in response_json["peJobs"]["results"]:

        # we try to create the company and we add the id of the job to the list_job_id_from_response
        company = createCompany(result["company"])
        list_job_id_from_response.append(result["job"]["id"])

        # if the company is not created, we skip the job, because it's not possible to create the job without the company
        # else we create the job
        if company is not None:
            createJob(result, company)

    # for each job in the matchas attribute in the response
    for result in response_json["matchas"]["results"]:

        # we try to create the company and we add the id of the job to the list_job_id_from_response
        company = createCompany(result["company"])
        list_job_id_from_response.append(result["job"]["id"])

        # if the company is not created, we skip the job, because it's not possible to create the job without the company
        # else we create the job
        if company is not None:
            createJob(result, company)

    # map the code of the job_codes from the database to a list of strings
    jobs_codes_request = list(map(lambda x: x.code, job_codes))

    # delete old jobs from database (jobs that are not in the response anymore)
    deleteOldJobs(list_job_id_from_response, jobs_codes_request)

    # create a new job_id_from_previous_request object with the list of job_ids from the response, and the job_codes associated
    JobIdFromPreviousRequest.objects.create(
        job_ids=list_job_id_from_response, job_codes=jobs_codes_request
    )


# create a company method
def createCompany(company):

    # if description, street, city, zip_code are empty, we set them to None
    if "description" in company:
        description = company["description"]
    else:
        description = None
    if getattr(company, "headquarter", None) is not None:
        street = company["headquarter"]["address"]
        city = company["headquarter"]["city"]
        zip_code = company["zipCode"]
    else:
        street = None
        city = None
        zip_code = None

    # if name is empty, we skip the company creation
    if "name" in company:

        # we update the company if it already exists, else we create it and return it
        company, created = Company.objects.update_or_create(
            name=company["name"],
            defaults={
                "description": description,
                "city": city,
                "street": street,
                "zip_code": zip_code,
            },
        )
        return company


# create a job method
def createJob(request, company):

    # if title, description, contract_type, start_date, schedule are empty, we set them to None
    if "title" in request:
        title = request["title"]
    else:
        title = None

    if "description" in request["job"]:
        description = request["job"]["description"]
    else:
        description = None

    if "contractType" in request["job"]:
        contract_type = request["job"]["contractType"]
    else:
        contract_type = None

    if "jobStartDate" in request["job"]:
        start_date = request["job"]["jobStartDate"]
    else:
        start_date = datetime.datetime.now()

    if "duration" in request["job"]:
        schedule = request["job"]["duration"]
    else:
        schedule = None

    # And if one of the fields is empty, we skip the job creation
    if title and description and contract_type and start_date and schedule:

        # we update the job if it already exists, else we create it and return it
        job, created = Job.objects.update_or_create(
            api_id=request["job"]["id"],
            defaults={
                "name": title,
                "description": description,
                "contract_type": contract_type,
                "start_date": start_date,
                "schedule": schedule,
                "company": company,
            },
        )

        # as we pass the company as a parameter, we attach the new job to the company and we return the job
        company.jobs.add(job)
        return job


# delete old jobs method
def deleteOldJobs(list_jobs_id_from_response, jobs_codes_request):

    # we get the list of job_ids from the database that are in the database
    old_jobs = JobIdFromPreviousRequest.objects.filter(
        job_codes__contains=jobs_codes_request
    )

    # for each job_id in the old_jobs
    for old_job in old_jobs:

        # for each id in the array of job_ids
        for old_job_id in old_job.job_ids:

            # if the id is not in the list of the response, we delete the job
            if old_job_id not in list_jobs_id_from_response:
                try:
                    job = Job.objects.get(api_id=old_job_id)
                    job.delete()
                    old_job.delete()
                except Job.DoesNotExist:
                    pass  # new job will be created
