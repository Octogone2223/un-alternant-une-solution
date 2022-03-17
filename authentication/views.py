from http.client import UNAUTHORIZED
import json
from multiprocessing import AuthenticationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from authentication.models import Company, Student, User, School
from .forms import CompanySignUpSerializer, UserSignInSerializer, UserSignUpSerializer, SchoolSignUpSerializer
from rest_framework import serializers

# Create your views here.


def sign_up(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        if bodyJson['accountType'] == '1':
            userSerializer = UserSignUpSerializer(data=bodyJson)
            companySerializer = CompanySignUpSerializer(data=bodyJson)
            try:
                userSerializer.__check_email__(bodyJson)
                if userSerializer.is_valid() and companySerializer.is_valid():
                    user = User.objects.create_user(
                        **userSerializer.validated_data
                    )
                    company = Company.objects.create(
                        **companySerializer.validated_data)

                    company.users.add(user)

                    return HttpResponse({'status': 'success'})
                else:
                    return HttpResponseBadRequest(json.dumps(userSerializer.errors + companySerializer.errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

            else:
                return render(request, 'sign_up.html', {'errors': UserSignUpSerializer(data=bodyJson).errors + CompanySerializer(data=bodyJson).errors})

        elif bodyJson['accountType'] == '2':
            userSerializer = UserSignUpSerializer(data=bodyJson)
            schoolSerializer = SchoolSignUpSerializer(data=bodyJson)

            try:
                userSerializer.__check_email__(bodyJson)
                is_valide_user = userSerializer.is_valid()
                is_valide_school = schoolSerializer.is_valid()
                if is_valide_user and is_valide_school:
                    user = User.objects.create_user(
                        **userSerializer.validated_data
                    )
                    school = School.objects.create(
                        **schoolSerializer.validated_data)

                    school.users.add(user)

                    return HttpResponse({'status': 'success'})
                else:
                    all_errors = dict(userSerializer.errors |
                                      schoolSerializer.errors)
                    print(all_errors)
                    return HttpResponseBadRequest(json.dumps(all_errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        elif bodyJson['accountType'] == '3':
            userSerializer = UserSignUpSerializer(data=bodyJson)
            try:
                userSerializer.__check_email__(bodyJson)
                if userSerializer.is_valid():
                    user = User.objects.create_user(
                        **userSerializer.validated_data
                    )
                    student = Student.objects.create(
                        user=user)
                    return HttpResponse({'status': 'success'})
                else:
                    return HttpResponseBadRequest(json.dumps(userSerializer.errors))
            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

    return render(request, 'sign_up.html')


def sign_in(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        userSerializer = UserSignInSerializer(data=bodyJson)

        if userSerializer.is_valid():
            user = authenticate(**userSerializer.validated_data)

            if user is not None:
                login(request, user)
                return HttpResponse({'status': 'success'})

            else:
                return HttpResponse({'status': 'failure'}, status=UNAUTHORIZED)

        else:
            return HttpResponseBadRequest(json.dumps(userSerializer.errors))

    return render(request, 'sign_in.html')


@login_required(login_url='sign_in')
def private(request):
    return render(request, 'private.html')

#


@login_required(login_url='sign_in')  # ! check
def sign_out(request):
    logout(request)
    return redirect('sign_in')
