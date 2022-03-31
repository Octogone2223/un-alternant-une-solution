from http.client import NOT_FOUND
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from authentication.models import Company, School, Student, User
from job.models import Job

# Create your views here.


# home view
def home(request):
    # get three latest published jobs, and the webpush options, and return them to the home page
    webpush = {"group": "alternant"}
    latest_jobs = Job.objects.all().order_by("-create_at")[:3]
    return render(request, "home.html", {"webpush": webpush, "jobs": latest_jobs})


# about view, just return the about page
def about(request):
    return render(request, "about.html")


# cgu view, just return the contact page
def cgu(request):
    return render(request, "CGU.html")


# legal mentions view, just return the legal mentions page
def legal(request):
    return render(request, "legal.html")


# policy view, just return the policy page
def policies(request):
    return render(request, "policies.html")


# student details view
def student_detail(request, student_id):

    try:

        # get the student by id from the url parameter
        student = list(
            Student.objects.filter(id=student_id).values(
                "id",
                "user_id",
                "birthday",
                "linkedin_url",
                "cv_path",
                "description",
                "linkedin_url",
            )
        )[0]

        # get the user associated with the student
        user_info = list(
            User.objects.filter(id=student["user_id"]).values(
                "id", "first_name", "last_name", "email", "extension_picture"
            )
        )[0]

        # return the student and the user to the student_detail page
        return render(
            request, "student_detail.html", {
                "student": student, "user_info": user_info}
        )

    # if the student does not exist, return a 404 error
    except Student.DoesNotExist:
        return HttpResponse("Student does not exist", status=NOT_FOUND)


# company details view
def company_detail(request, company_id):
    try:

        # get the company by id from the url parameter
        company = list(
            Company.objects.filter(id=company_id).values(
                "id", "name", "description", "city", "street", "zip_code"
            )
        )[0]

        # return the company infor to the company_detail page
        return render(request, "company_detail.html", {"company": company})

    # if the company does not exist, return a 404 error
    except Company.DoesNotExist:
        return HttpResponse("Company does not exist", status=NOT_FOUND)


# school details view
def school_detail(request, school_id):
    try:

        # get the school by id from the url parameter
        school = list(
            School.objects.filter(id=school_id).values(
                "id", "name", "description", "city", "street", "zip_code"
            )
        )[0]

        # return the school infor to the school_detail page
        return render(request, "school_detail.html", {"school": school})

    # if the school does not exist, return a 404 error
    except School.DoesNotExist:
        return HttpResponse("School does not exist", status=NOT_FOUND)


# profile view (must be logged in)
@login_required
def profile(request):

    # get the user from the request
    user_data = list(User.objects.filter(id=request.user.id).values())[0]
    user_type = request.user.getUserType()
    data = None

    # if the user is a student, get the student data
    if user_type == "Student":
        data = list(
            Student.objects.filter(user=request.user).values(
                "id",
                "user_id",
                "birthday",
                "linkedin_url",
                "cv_path",
                "description",
                "course__name",
            )
        )[0]

    # if the user is a company, get the company data
    elif user_type == "Company":
        data = list(Company.objects.filter(users=request.user).values())[0]

    # if the user is a school, get the school data
    else:
        data = list(School.objects.filter(users=request.user).values())[0]

    # return the user data to the profile page
    return render(
        request, "profile.html", {"data": data,
                                  "user": user_data, "userType": user_type}
    )
