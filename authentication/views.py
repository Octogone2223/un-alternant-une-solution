import base64
import codecs
import datetime
from http.client import UNAUTHORIZED
import json
from multiprocessing import AuthenticationError
import os
import secrets
import string
from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from authentication.models import Company, Student, User, School
from .serializers import (
    CompanySerializer,
    CompanySignUpSerializer,
    SchoolSerializer,
    UserSerializer,
    UserSignInSerializer,
    UserSignUpSerializer,
    SchoolSignUpSerializer,
    StudentSerializer,
)
from rest_framework import serializers
from mailjet_rest import Client

# Create your views here.
api_key = "1291d676337d606bd0888a8ae018f72f"
api_secret = "c216714c0f3ed0af7d3b915b86df7cb9"


def sign_up(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        if bodyJson["accountType"] == "1":
            companySerializer = CompanySignUpSerializer(data=bodyJson)
            try:
                companySerializer.__check_email__(bodyJson)
                if companySerializer.is_valid():
                    user = User.objects.create_user(
                        companySerializer.validated_data["email"],
                        companySerializer.validated_data["password"],
                    )

                    user.last_name = companySerializer.validated_data["last_name"]
                    user.first_name = companySerializer.validated_data["first_name"]

                    user.save()

                    company = Company.objects.create(
                        name=companySerializer.validated_data["name"],
                        description=companySerializer.validated_data["description"],
                        city=companySerializer.validated_data["city"],
                        street=companySerializer.validated_data["street"],
                        zip_code=companySerializer.validated_data["zip_code"],
                    )

                    company.users.add(user)

                    company.save()

                    return HttpResponse({"status": "success"})
                else:
                    return HttpResponseBadRequest(json.dumps(companySerializer.errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        elif bodyJson["accountType"] == "2":
            schoolSerializer = SchoolSignUpSerializer(data=bodyJson)

            try:
                schoolSerializer.__check_email__(bodyJson)
                if schoolSerializer.is_valid():
                    user = User.objects.create_user(
                        schoolSerializer.validated_data["email"],
                        schoolSerializer.validated_data["password"],
                    )

                    user.last_name = schoolSerializer.validated_data["last_name"]
                    user.first_name = schoolSerializer.validated_data["first_name"]

                    user.save()

                    school = School.objects.create(
                        name=schoolSerializer.validated_data["name"],
                        city=schoolSerializer.validated_data["city"],
                        street=schoolSerializer.validated_data["street"],
                        zip_code=schoolSerializer.validated_data["zip_code"],
                    )

                    school.users.add(user)

                    return HttpResponse({"status": "success"})
                else:
                    return HttpResponseBadRequest(json.dumps(schoolSerializer.errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        elif bodyJson["accountType"] == "3":
            userSerializer = UserSignUpSerializer(data=bodyJson)

            try:
                userSerializer.__check_email__(bodyJson)
                if userSerializer.is_valid():
                    user = User.objects.create_user(**userSerializer.validated_data)

                    student = Student.objects.create(user=user)

                    return HttpResponse({"status": "success"})
                else:
                    return HttpResponseBadRequest(json.dumps(userSerializer.errors))

            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

    return render(request, "sign_up.html")


def sign_in(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        userSerializer = UserSignInSerializer(data=bodyJson)

        if userSerializer.is_valid():
            user = authenticate(**userSerializer.validated_data)

            if user is not None:
                login(request, user)
                return HttpResponse({"status": "success"})

            else:
                return HttpResponse({"status": "failure"}, status=UNAUTHORIZED)

        else:
            return HttpResponseBadRequest(json.dumps(userSerializer.errors))

    return render(request, "sign_in.html")


@login_required
def private(request):
    return render(request, "private.html")


@login_required
def sign_out(request):
    logout(request)
    return redirect("/")


@login_required
def user(request):
    if request.method == "POST":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        userType = bodyJson["userType"]
        userSerializer = UserSerializer(data=bodyJson["userSend"])

        bodyJson["userSend"]["updated_at"] = datetime.datetime.now()

        try:

            if (
                userType == "Company"
                and userSerializer.is_valid()
                and CompanySerializer(data=bodyJson["dataSend"]).is_valid()
            ):

                idUser = bodyJson["userSend"]["id"]
                companySerializer = CompanySerializer(data=bodyJson["dataSend"])

                try:
                    if companySerializer.is_valid():
                        User.objects.filter(id=idUser).update(**bodyJson["userSend"])
                        Company.objects.filter(id=bodyJson["dataSend"]["id"]).update(
                            **bodyJson["dataSend"]
                        )
                        return JsonResponse({"status": "success"})
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(companySerializer.errors)
                        )
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

            elif (
                userType == "School"
                and userSerializer.is_valid()
                and SchoolSerializer(data=bodyJson["dataSend"]).is_valid()
            ):

                idUser = bodyJson["userSend"]["id"]
                schoolSerializer = SchoolSerializer(data=bodyJson["dataSend"])
                print(schoolSerializer.is_valid())
                try:
                    if schoolSerializer.is_valid():
                        User.objects.filter(id=idUser).update(**bodyJson["userSend"])
                        School.objects.filter(id=bodyJson["dataSend"]["id"]).update(
                            **bodyJson["dataSend"]
                        )
                        return JsonResponse({"status": "success"})
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(schoolSerializer.errors)
                        )
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

            else:
                idUser = bodyJson["userSend"]["id"]
                cv_path = bodyJson["dataSend"]["cv_path"]
                if bodyJson["dataSend"]["cv_file"]:
                    pathCv = f"authentication/files/cv/public_{idUser}.{cv_path}"
                    text_file = open(f"{settings.BASE_DIR}/{pathCv}", "wb")
                    text_file.write(base64.b64decode(bodyJson["dataSend"]["cv_file"]))
                    text_file.close()

                bodyJson["dataSend"].pop("cv_file")
                studentSerializer = StudentSerializer(data=bodyJson["dataSend"])
                try:
                    if studentSerializer.is_valid():
                        # Model.objects.filter(id = 223).update(field1 = 2)
                        User.objects.filter(id=idUser).update(**bodyJson["userSend"])
                        Student.objects.filter(id=bodyJson["dataSend"]["id"]).update(
                            **bodyJson["dataSend"]
                        )
                        return JsonResponse({"status": "success"})
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(studentSerializer.errors)
                        )
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

        except serializers.ValidationError as e:
            return HttpResponseBadRequest(json.dumps(e.detail))

    userJSON = list(User.objects.filter(id=request.user.id).values())[0]
    userType = request.user.getUserType()
    data = None

    if userType == "Student":
        data = list(Student.objects.filter(user=request.user).values())[0]
    elif userType == "Company":
        data = list(Company.objects.filter(user=request.user).company.values())[0]
    else:
        data = list(School.objects.filter(user=request.user).school.values())[0]
    return JsonResponse({"data": data, "user": userJSON, "userType": userType})


@login_required
def updatePassword(request):
    if request.method == "PATCH":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        try:
            user = User.objects.get(pk=bodyJson["userSend"]["id"])

            if user.check_password(bodyJson["userSend"]["passwordActual"]):
                user.set_password(bodyJson["userSend"]["newPassword"])
                user.save()
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse(
                    {
                        "status": "none",
                        "errors": {
                            "current": ["Le mot de passe actuel ne correspond pas"]
                        },
                    }
                )

        except User.DoesNotExist:
            raise Http404("Given query not found....")


# TODO: Faire le fameux DjangoGuardian (GET pour tous le monde et POST pour les connectés)
# @login_required(login_url='sign_in')
def cvPublic(request, id):

    try:
        user = Student.objects.get(user=id)
        try:
            pathCv = f"authentication/files/cv/public_{id}.{user.cv_path}"
            return FileResponse(open(f"{settings.BASE_DIR}/{pathCv}", "rb"))
        except IOError:
            return HttpResponse({"notExist": "failure"}, status=UNAUTHORIZED)
    except Student.DoesNotExist:
        return HttpResponse({"notExist": "failure"}, status=UNAUTHORIZED)


# TODO: Faire le fameux DjangoGuardian (GET pour tous le monde et POST pour les connectés)


def photo(request, id):

    if request.method == "PUT":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        user = User.objects.get(id=id)
        if os.path.exists(
            f"{settings.BASE_DIR}/authentication/files/picture/{id}.{user.extension_picture}"
        ):
            os.remove(
                f"{settings.BASE_DIR}/authentication/files/picture/{id}.{user.extension_picture}"
            )

        pathCv = f'authentication/files/picture/{id}.{bodyJson["extensionFile"]}'
        text_file = open(f"{settings.BASE_DIR}/{pathCv}", "wb")
        text_file.write(base64.b64decode(bodyJson["filePhoto"]))
        text_file.close()

        User.objects.filter(id=id).update(extension_picture=bodyJson["extensionFile"])
        return JsonResponse({"status": "success"})

    try:
        user = User.objects.get(id=id)
        try:
            pathImg = f"authentication/files/picture/{id}.{user.extension_picture}"
            return FileResponse(open(f"{settings.BASE_DIR}/{pathImg}", "rb"))
        except IOError:
            return FileResponse(
                open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb")
            )
    except User.DoesNotExist:
        return FileResponse(open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb"))


def school_photo(request, id):
    if request.method == "PUT":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        school = School.objects.get(id=id)
        if os.path.exists(
            f"{settings.BASE_DIR}/authentication/files/picture/school/{id}.{school.extension_picture}"
        ):
            os.remove(
                f"{settings.BASE_DIR}/authentication/files/picture/school/{id}.{school.extension_picture}"
            )

        pathCv = f'authentication/files/picture/school/{id}.{bodyJson["extensionFile"]}'
        text_file = open(f"{settings.BASE_DIR}/{pathCv}", "wb")
        text_file.write(base64.b64decode(bodyJson["fileEntity"]))
        text_file.close()

        School.objects.filter(id=id).update(extension_picture=bodyJson["extensionFile"])
        return JsonResponse({"status": "success"})

    try:
        school = School.objects.get(id=id)
        try:
            pathImg = (
                f"authentication/files/picture/school/{id}.{school.extension_picture}"
            )
            return FileResponse(open(f"{settings.BASE_DIR}/{pathImg}", "rb"))
        except IOError:
            return HttpResponse({"notExist": "failure"}, status=UNAUTHORIZED)
    except School.DoesNotExist:
        return FileResponse(open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb"))


def company_photo(request, id):
    if request.method == "PUT":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        company = Company.objects.get(id=id)
        if os.path.exists(
            f"{settings.BASE_DIR}/authentication/files/picture/company/{id}.{company.extension_picture}"
        ):
            os.remove(
                f"{settings.BASE_DIR}/authentication/files/picture/company/{id}.{company.extension_picture}"
            )

        pathCv = (
            f'authentication/files/picture/company/{id}.{bodyJson["extensionFile"]}'
        )
        text_file = open(f"{settings.BASE_DIR}/{pathCv}", "wb")
        text_file.write(base64.b64decode(bodyJson["fileEntity"]))
        text_file.close()

        Company.objects.filter(id=id).update(
            extension_picture=bodyJson["extensionFile"]
        )
        return JsonResponse({"status": "success"})
    try:
        company = Company.objects.get(id=id)
        try:
            pathImg = (
                f"authentication/files/picture/company/{id}.{company.extension_picture}"
            )
            return FileResponse(open(f"{settings.BASE_DIR}/{pathImg}", "rb"))
        except IOError:
            return HttpResponse({"notExist": "failure"}, status=UNAUTHORIZED)
    except Company.DoesNotExist:
        return FileResponse(open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb"))


def forgotPassword(request):

    if request.method == "POST":

        body = request.body.decode("utf-8")
        bodyJson = json.loads(body)

        try:
            user = User.objects.get(email=bodyJson["email"])

            alphabet = string.ascii_letters + string.digits
            password = "".join(secrets.choice(alphabet) for i in range(10))
            user.set_password(password)
            user.save()

            mailjet = Client(auth=(api_key, api_secret), version="v3.1")
            data = {
                "Messages": [
                    {
                        "From": {"Email": "tegak41827@moonran.com", "Name": "John"},
                        "To": [
                            {
                                "Email": user.email,
                                "Name": f"{user.first_name} {user.last_name}",
                            }
                        ],
                        "Subject": "1Alternant1Solution - Nouveau Mot de Passe",
                        "TextPart": f"Bonjour {user.first_name} {user.last_name},1Alternant1Solution est une plateforme de mise en relation entre étudiants et entreprises. Nous croyons que c’est avec les jeunes que l’avenir se construit, alors merci d'être dans notre communauté ! Voici le nouveau mot de passe : {password} Cordialement, Tom Leveque",
                        "HTMLPart": f'<p data-pm-slice="1 1 []">Bonjour {user.first_name} {user.last_name},</p><p data-pm-slice="1 1 []">1Alternant1Solution est une plateforme de mise en relation entre &eacute;tudiants et entreprises. Nous croyons que c&rsquo;est avec les jeunes que l&rsquo;avenir se construit, alors merci d\'&ecirc;tre dans notre communaut&eacute; !</p><p data-pm-slice="1 1 []">Voici le nouveau mot de passe : {password}</p><p data-pm-slice="1 1 []">Cordialement,</p><p data-pm-slice="1 1 []">Tom Leveque</p>',
                        "CustomID": "MotDePasseOublie",
                    }
                ]
            }
            result = mailjet.send.create(data=data)
            print(result.json())
            if str(result.status_code) == "200":
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse(
                    {
                        "status": "none",
                        "message": "Il y a eu un problème lors de l'envoie du mail",
                    }
                )

        except User.DoesNotExist:
            return JsonResponse(
                {"status": "none", "message": "Aucun utilisateur trouvé"}
            )
