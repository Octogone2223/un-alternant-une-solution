from http.client import UNAUTHORIZED
import json
from multiprocessing import AuthenticationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from authentication.models import Company, Student, User, School
from .serializers import CompanySignUpSerializer, UserSignInSerializer, UserSignUpSerializer, SchoolSignUpSerializer
from rest_framework import serializers

# Create your views here.


def sign_up(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        if bodyJson['accountType'] == '1':
            companySerializer = CompanySignUpSerializer(data=bodyJson)
            try:
                companySerializer.__check_email__(bodyJson)
                if companySerializer.is_valid():
                    user = User.objects.create_user(companySerializer.validated_data['email'],
                                                    companySerializer.validated_data['password'],
                                                    )

                    user.last_name = companySerializer.validated_data['last_name']
                    user.first_name = companySerializer.validated_data['first_name']

                    user.save()

                    company = Company.objects.create(
                        name=companySerializer.validated_data['name'],
                        description=companySerializer.validated_data['description'],
                        city=companySerializer.validated_data['city'],
                        street=companySerializer.validated_data['street'],
                        zip_code=companySerializer.validated_data['zip_code'],
                    )

                    company.users.add(user)

                    return HttpResponse({'status': 'success'})
                else:
                    return HttpResponseBadRequest(json.dumps(companySerializer.errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        elif bodyJson['accountType'] == '2':
            schoolSerializer = SchoolSignUpSerializer(data=bodyJson)

            try:
                schoolSerializer.__check_email__(bodyJson)
                if schoolSerializer.is_valid():
                    user = User.objects.create_user(schoolSerializer.validated_data['email'],
                                                    schoolSerializer.validated_data['password'],
                                                    )

                    user.last_name = schoolSerializer.validated_data['last_name']
                    user.first_name = schoolSerializer.validated_data['first_name']

                    user.save()

                    school = School.objects.create(
                        name=schoolSerializer.validated_data['name'],
                        city=schoolSerializer.validated_data['city'],
                        street=schoolSerializer.validated_data['street'],
                        zip_code=schoolSerializer.validated_data['zip_code'],
                    )

                    school.users.add(user)

                    return HttpResponse({'status': 'success'})
                else:
                    return HttpResponseBadRequest(json.dumps(schoolSerializer.errors))

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


@login_required
def private(request):
    return render(request, 'private.html')


@login_required(login_url='/')
def sign_out(request):
    logout(request)
    return redirect(reverse('app:home'))
