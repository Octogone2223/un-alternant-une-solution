from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from authentication.models import Company, School, Student, User
# Create your views here.


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


@login_required(login_url='authentication:sign_in')
def profile(request):

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    data = None

    if userType == 'Student':
        data = list(Student.objects.filter(user=request.user).values())[0]
    elif userType == 'Company':
        data = list(Company.objects.filter(
            user_companies=request.user).values())[0]
        pass
    else:
        data = list(School.objects.filter(users=request.user).values())[0]
    return render(request, "profile.html", {'data': data, 'user': userJSON, 'userType': userType})
