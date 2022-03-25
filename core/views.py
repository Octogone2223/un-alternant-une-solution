from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from authentication.models import Company, School, Student, User
from job.models import Job

# Create your views here.


def home(request):
    webpush = {"group": "alternant"}
    latest_jobs = Job.objects.all().order_by("-create_at")[:3]
    return render(request, "home.html", {"webpush": webpush, "jobs": latest_jobs})


def about(request):
    return render(request, "about.html")


def cgu(request):
    return render(request, "CGU.html")


def legal(request):
    return render(request, "legal.html")


def policies(request):
    return render(request, "policies.html")


def student_detail(request, student_id):
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

    user_info = list(
        User.objects.filter(id=student["user_id"]).values(
            "id", "first_name", "last_name", "email", "extension_picture"
        )
    )[0]

    return render(
        request, "student_detail.html", {"student": student, "user_info": user_info}
    )


def company_detail(request, company_id):
    company = list(
        Company.objects.filter(id=company_id).values(
            "id", "name", "description", "city", "street", "zip_code"
        )
    )[0]

    return render(request, "company_detail.html", {"company": company})


def school_detail(request, school_id):
    school = list(
        School.objects.filter(id=school_id).values(
            "id", "name", "description", "city", "street", "zip_code"
        )
    )[0]

    return render(request, "school_detail.html", {"school": school})


@login_required(login_url="authentication:sign_in")
def profile(request):

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    data = None

    if userType == "Student":
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
    elif userType == "Company":
        data = list(Company.objects.filter(users=request.user).values())[0]
    else:
        data = list(School.objects.filter(users=request.user).values())[0]
    return render(
        request, "profile.html", {"data": data, "user": userJSON, "userType": userType}
    )
