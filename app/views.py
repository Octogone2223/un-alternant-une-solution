from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    return render(request, 'home.html')


@login_required(login_url='authentication:sign_in')
def profile(request):
    return render(request, "profile.html", {'typeUser': request.user.getUserType()})
