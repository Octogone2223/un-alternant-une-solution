from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from authentication.models import Company, School, Student, User
# Create your views here.


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def student_detail(request, student_id):
    student = list(Student.objects.filter(
        id=student_id).values('id', 'user_id', 'birthday', 'linkedin_url', 'cv_path', 'description'))[0]

    user_info = list(User.objects.filter(
        id=student['user_id']).values('id', 'first_name', 'last_name', 'email', 'extension_picture'))[0]

    return render(request, 'student_detail.html', {'student': student, 'user_info': user_info})


def company_detail(request, company_id):
    company = list(Company.objects.filter(id=company_id).values(
        'id', 'name', 'description', 'city', 'street', 'zip_code'))[0]

    return render(request, 'company_detail.html', {'company': company})


def school_detail(request, school_id):
    school = list(School.objects.filter(id=school_id).values(
        'id', 'name', 'description', 'city', 'street', 'zip_code'))[0]

    return render(request, 'school_detail.html', {'school': school})


@login_required(login_url='authentication:sign_in')
def profile(request):

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    data = None

    if userType == 'Student':
        data = list(Student.objects.filter(user=request.user).values())[0]
    elif userType == 'CompanyUser':
        data = list(Company.objects.filter(
            user_companies=request.user).values())[0]
        pass
    else:
        data = list(School.objects.filter(users=request.user).values())[0]
    return render(request, "profile.html", {'data': data, 'user': userJSON, 'userType': userType})
