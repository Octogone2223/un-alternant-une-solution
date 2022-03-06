from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from authentication.models import Company, User

# Create your views here.


def sign_up(request):
    if request.method == 'GET':
        return render(request, 'sign_up.html')

    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = User.objects.create_user(email=email, password=password)

            company = Company()
            company.name = request.POST.get('company_name', 'company_name')
            company.description = request.POST.get(
                'company_description', 'company_description')
            company.city = request.POST.get('company_city', 'company_city')
            company.street = request.POST.get(
                'company_street', 'company_street')
            company.zip_code = request.POST.get('zip_code', 'zip_code')
            company.user = user

            user.save()
            company.save()

        except Exception as e:
            return render(request, 'sign_up.html', {'error': e})

        login(request, user)
        request.session.set_expiry(1 * 24 * 60 * 60)  # 1 day
        return redirect('private')


def sign_in(request):
    if request.method == 'GET':
        return render(request, 'sign_in.html')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            request.session.set_expiry(1 * 24 * 60 * 60)  # 1 day
            return redirect('private')

        else:
            return redirect('sign_in')


@login_required(login_url='sign_in')
def private(request):
    return render(request, 'private.html')


@login_required(login_url='sign_in')
def sign_out(request):
    logout(request)
    return redirect('sign_in')
