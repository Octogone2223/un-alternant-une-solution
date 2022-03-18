import base64
import codecs
import datetime
from http.client import UNAUTHORIZED
import json
from multiprocessing import AuthenticationError
import os
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from authentication.models import Company, Student, User, UserCompany
from job.models import Job
from .forms import CompanySerializer, StudentSerializer, UserSignInSerializer, UserSignUpSerializer, SchoolSerializer
from rest_framework import serializers

# Create your views here.


def sign_up(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        if bodyJson['accountType'] == '1':
            userSerializer = UserSignUpSerializer(data=bodyJson)
            companySerializer = CompanySerializer(data=bodyJson)
            if userSerializer.is_valid() and companySerializer.is_valid():
                user = User.objects.create_user(userSerializer.valitade_data)
                company = Company.objects.create(
                    companySerializer.validated_data)
                company.user = user.save()
                company.save()
                login(request, user)
                return redirect('sign_in')
            else:
                return render(request, 'sign_up.html', {'errors': UserSignUpSerializer(data=bodyJson).errors + CompanySerializer(data=bodyJson).errors})

        elif bodyJson['accountType'] == '2':
            if UserSignUpSerializer(data=bodyJson).is_valid() and SchoolSerializer(data=bodyJson).is_valid():
                user = UserSignUpSerializer(data=bodyJson)
                school = SchoolSerializer(data=bodyJson)
                school.user = user.save()
                school.save()
                login(request, user)
                return redirect('sign_in')
            else:
                return render(request, 'sign_up.html', {'errors': UserSignUpSerializer(data=bodyJson).errors + SchoolSerializer(data=bodyJson).errors})

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


@login_required(login_url='sign_in')
def user(request):
    if request.method == 'POST':

        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        # if UserSignUpSerializer(data=bodyJson).is_valid() and SchoolSerializer(data=bodyJson).is_valid():

        userSerializer = UserSignUpSerializer(data=bodyJson["userSend"])

        bodyJson["updated_at"] = datetime.datetime.now()

        try:

            if userSerializer.is_valid() and CompanySerializer(data=bodyJson["dataSend"]).is_valid():
                pass
            elif userSerializer.is_valid() and SchoolSerializer(data=bodyJson["dataSend"]).is_valid():
                pass
            else:
                idUser = bodyJson["userSend"]['id']

                if (bodyJson["dataSend"]['cv_file']):
                    pathCv = f'authentication/files/cv/public_{idUser}.pdf'
                    text_file = open(f'{settings.BASE_DIR}/{pathCv}', "wb")
                    text_file.write(base64.b64decode(
                        bodyJson["dataSend"]['cv_file']))
                    text_file.close()

                    bodyJson["dataSend"]['cv_path'] = f'cv/public_{idUser}.pdf'

                bodyJson["dataSend"].pop("cv_file")
                studentSerializer = StudentSerializer(
                    data=bodyJson["dataSend"])
                try:
                    if (studentSerializer.is_valid()):
                        # Model.objects.filter(id = 223).update(field1 = 2)
                        User.objects.filter(id=idUser).update(
                            **bodyJson["userSend"])
                        Student.objects.filter(id=bodyJson["dataSend"]['id']).update(
                            **bodyJson["dataSend"])
                        return JsonResponse({'status': 'success'})
                    else:
                        return HttpResponseBadRequest(json.dumps(studentSerializer.errors))
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

        except serializers.ValidationError as e:
            return HttpResponseBadRequest(json.dumps(e.detail))

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    data = None

    if userType == 'Student':
        data = list(Student.objects.filter(user=request.user).values())[0]
    elif userType == 'Company':
        data = list(UserCompany.objects.filter(
            user=request.user).company.values())[0]
    else:
        data = list(UserCompany.objects.filter(
            user=request.user).school.values())[0]
    return JsonResponse({'data': data, 'user': userJSON, 'userType': userType})


# TODO: Faire le fameux DjangoGuardian (GET pour tous le monde et POST pour les connectés)
# @login_required(login_url='sign_in')
def cvPublic(request, id):

    try:
        pathCv = f'authentication/files/cv/public_{id}.pdf'
        return FileResponse(open(f'{settings.BASE_DIR}/{pathCv}', "rb"))
    except IOError:
        return HttpResponse({'notExist': 'failure'}, status=UNAUTHORIZED)

# TODO: Faire le fameux DjangoGuardian (GET pour tous le monde et POST pour les connectés)


def photo(request, id):

    if request.method == 'PUT':

        body = request.body.decode('utf-8')
        bodyJson = json.loads(body)

        user = User.objects.get(id=id)
        os.remove(
            f'{settings.BASE_DIR}/authentication/files/picture/{id}.{user.extension_picture}')

        pathCv = f'authentication/files/picture/{id}.{bodyJson["extensionFile"]}'
        text_file = open(f'{settings.BASE_DIR}/{pathCv}', "wb")
        text_file.write(base64.b64decode(bodyJson["filePhoto"]))
        text_file.close()

        User.objects.filter(id=id).update(
            extension_picture=bodyJson["extensionFile"])
        return JsonResponse({'status': 'success'})

    user = User.objects.get(id=id)
    try:
        pathImg = f'authentication/files/picture/{id}.{user.extension_picture}'
        return FileResponse(open(f'{settings.BASE_DIR}/{pathImg}', "rb"))
    except IOError:
        return HttpResponse({'notExist': 'failure'}, status=UNAUTHORIZED)
