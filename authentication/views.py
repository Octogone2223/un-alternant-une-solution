import base64
import datetime
from http.client import BAD_REQUEST, NOT_FOUND, UNAUTHORIZED, OK
import json
import os
import secrets
import string
from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
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


# Sign up view
def sign_up(request):

    # if user submit the form to sign up
    if request.method == "POST":

        # Get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        # Check if the user is a company
        if body_json["accountType"] == "1":

            # Serialize the data company
            company_serializer = CompanySignUpSerializer(data=body_json)

            try:

                # Check if the data is valid
                if company_serializer.is_valid():

                    # Create user from the data company whith the build in create method from django
                    user = User.objects.create_user(
                        company_serializer.validated_data["email"],
                        company_serializer.validated_data["password"],
                    )

                    # Update the user with the data company and save it
                    user.last_name = company_serializer.validated_data["last_name"]
                    user.first_name = company_serializer.validated_data["first_name"]
                    user.save()

                    # Create the company from the data company
                    company = Company.objects.create(
                        name=company_serializer.validated_data["name"],
                        description=company_serializer.validated_data["description"],
                        city=company_serializer.validated_data["city"],
                        street=company_serializer.validated_data["street"],
                        zip_code=company_serializer.validated_data["zip_code"],
                    )

                    # Insert the user in the company and save it
                    company.users.add(user)
                    company.save()

                    # Return an HTTP Status code success
                    return JsonResponse({"status": "success"}, status=OK)

                # If the data is not valid, return an HTTP Status code bad request with the errors
                else:
                    return HttpResponseBadRequest(json.dumps(company_serializer.errors))

            # If the email is already used, return an HTTP Status code bad request with the errors
            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        # Check if the user is a company
        elif body_json["accountType"] == "2":

            # Serialize the data school
            school_serializer = SchoolSignUpSerializer(data=body_json)

            try:

                # Check if the data is valid
                if school_serializer.is_valid():

                    # Create user from the data school whith the build in create method from django
                    user = User.objects.create_user(
                        school_serializer.validated_data["email"],
                        school_serializer.validated_data["password"],
                    )

                    # Update the user with the data school and save it
                    user.last_name = school_serializer.validated_data["last_name"]
                    user.first_name = school_serializer.validated_data["first_name"]
                    user.save()

                    # Create the school from the data school
                    school = School.objects.create(
                        name=school_serializer.validated_data["name"],
                        city=school_serializer.validated_data["city"],
                        street=school_serializer.validated_data["street"],
                        zip_code=school_serializer.validated_data["zip_code"],
                    )

                    # Insert the user in the school and save it
                    school.users.add(user)
                    school.save()

                    # Return an HTTP Status code success
                    return JsonResponse({"status": "success"}, status=OK)

                # If the data is not valid, return an HTTP Status code bad request with the errors
                else:
                    return HttpResponseBadRequest(json.dumps(school_serializer.errors))

            # If the email is already used, return an HTTP Status code bad request with the errors
            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

        # Check if the user is a student
        elif body_json["accountType"] == "3":

            # Serialize the data student
            user_serializer = UserSignUpSerializer(data=body_json)

            try:

                # Check if the data is valid
                if user_serializer.is_valid():

                    # Create user from the data (destructure the data) whith the build in create method from django
                    user = User.objects.create_user(
                        **user_serializer.validated_data)

                    # Create the student from the data student
                    Student.objects.create(user=user)

                    # Return an HTTP Status code success
                    return JsonResponse({"status": "success"}, status=OK)

                # If the data is not valid, return an HTTP Status code bad request with the errors
                else:
                    return HttpResponseBadRequest(json.dumps(user_serializer.errors))

            # If the email is already used, return an HTTP Status code bad request with the errors
            except serializers.ValidationError as e:
                return HttpResponseBadRequest(json.dumps(e.detail))

    # If the method is not POST, return the sign up page
    return render(request, "sign_up.html")


# Sign in view
def sign_in(request):

    # If the user submit the form to sign in
    if request.method == "POST":

        # Get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        # Serialize the user data
        user_serializer = UserSignInSerializer(data=body_json)

        # Check if the data is valid
        if user_serializer.is_valid():

            # Authenticate the user with the build in authenticate method from django
            user = authenticate(**user_serializer.validated_data)

            # If the user credentials are valid, log the user in and redirect him to the home page
            if user is not None:
                login(request, user)
                return JsonResponse({"status": "success"})

            # If the user credentials are not valid, return an HTTP Status code UNAUTHORIZED (NOT RETURN ERRORS !)
            else:
                return JsonResponse({"status": "failure"}, status=UNAUTHORIZED)

        # If the data form is not valid, return an HTTP Status code bad request with the errors
        else:
            return HttpResponseBadRequest(json.dumps(user_serializer.errors))

    # If the method is not POST, return the sign in page
    return render(request, "sign_in.html")


# Sign out view (must be logged in)
@login_required
def sign_out(request):

    # Log the user out and redirect him to the home page
    logout(request)
    return redirect("/")


# profile view (must be logged in)
@login_required
def user(request):

    # if the user update his profile
    if request.method == "POST":

        # Get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)
        # Serialize the user data
        userType = body_json["userType"]
        user_serializer = UserSerializer(data=body_json["userSend"])

        # Update the body with a new attribute 'update_at' using the current date
        body_json["userSend"]["updated_at"] = datetime.datetime.now()

        user_id = request.user.id

        try:
            # Check if it's a company and the data is valid
            if (
                userType == "company" and user_serializer.is_valid() and CompanySerializer(
                    data=body_json["dataSend"]).is_valid()
            ):

                # serialize the data company
                company_serializer = CompanySerializer(
                    data=body_json["dataSend"])

                try:

                    # Check if the data is valid
                    if company_serializer.is_valid():

                        # Update the user and the company with their serializer
                        User.objects.filter(id=user_id).update(
                            **user_serializer.validated_data
                        )
                        Company.objects.filter(id=body_json["dataSend"]["id"]).update(
                            **company_serializer.validated_data
                        )

                        # Return an HTTP Status code success
                        return JsonResponse({"status": "success"}, status=OK)

                    # If the data company is not valid, return an HTTP Status code bad request with the errors
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(company_serializer.errors)
                        )

                # if any error is raised by the serializer validator, return an HTTP Status code bad request with the errors
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

            # Check if it's a school and the data is valid
            elif (
                userType == "school" and user_serializer.is_valid(
                ) and SchoolSerializer(data=body_json["dataSend"]).is_valid()
            ):

                # serialize the data school
                school_serializer = SchoolSerializer(
                    data=body_json["dataSend"])

                try:

                    # Check if the data is valid
                    if school_serializer.is_valid():

                        # Update the user and the school with their serializer
                        User.objects.filter(id=user_id).update(
                            **user_serializer.validated_data
                        )
                        School.objects.filter(id=body_json["dataSend"]["id"]).update(
                            **school_serializer.validated_data
                        )

                        # Return an HTTP Status code success
                        return JsonResponse({"status": "success"}, status=OK)

                    # If the data school is not valid, return an HTTP Status code bad request with the errors
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(school_serializer.errors)
                        )

                # if any error is raised by the serializer validator, return an HTTP Status code bad request with the errors
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))

            # Check if it's a student and the data is valid
            elif user_serializer.is_valid():

                # get the path of the actual profile picture
                cv_path = body_json["dataSend"]["cv_path"]
                # get File Base64 object
                cv_file = body_json["dataSend"]["cv_file"]

                body_json["dataSend"].pop("cv_file")
                studentSerializer = StudentSerializer(
                    data=body_json["dataSend"])

                try:

                    # Check if the data is valid
                    if studentSerializer.is_valid():

                        # Update the user and the student with their serializer
                        User.objects.filter(id=user_id).update(
                            **user_serializer.validated_data
                        )
                        Student.objects.filter(id=body_json["dataSend"]["id"]).update(
                            **studentSerializer.validated_data
                        )

                        # If the user has a profile picture, update it
                        if cv_path is not None and cv_file is not None:

                            student: Student = Student.objects.get(
                                id=body_json["dataSend"]["id"])
                            student.cv.save(
                                f"public_{user_id}.{cv_path}", ContentFile(base64.b64decode(cv_file)), save=True)
                            student.save()

                        # Return an HTTP Status code success
                        return JsonResponse({"status": "success"}, status=OK)

                    # If the data student is not valid, return an HTTP Status code bad request with the errors
                    else:
                        return HttpResponseBadRequest(
                            json.dumps(studentSerializer.errors)
                        )

                # if any error is raised by the serializer validator, return an HTTP Status code bad request with the errors
                except serializers.ValidationError as e:
                    return HttpResponseBadRequest(json.dumps(e.detail))
            else:
                raise Http404("N'existe Pas")
        # if any other error is raised by the serializer validator, return an HTTP Status code bad request with the errors
        except serializers.ValidationError as e:
            return HttpResponseBadRequest(json.dumps(e.detail))

    # If the method is not POST, get all the user data and return it
    user_data = list(User.objects.filter(id=request.user.id).values())[0]
    user_type = request.user.getUserType()
    data = None

    if user_type == "student":
        data = list(Student.objects.filter(user=request.user).values())[0]

    elif user_type == "company":
        data = list(Company.objects.filter(
            user=request.user).company.values())[0]

    else:
        data = list(School.objects.filter(
            user=request.user).school.values())[0]

    # return a json with the user data and the data of the user
    return JsonResponse({"data": data, "user": user_data, "userType": user_type})


# update the user password (must be logged in)
@ login_required
def updatePassword(request):
    if request.method == "PATCH":

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:

            # get the user of the request
            user = User.objects.get(pk=request.user.id)

            # check if the password is valid with the built-in django function, if valid ...
            if user.check_password(body_json["userSend"]["passwordActual"]):

                # ... update the password with the new one and return an HTTP Status code success
                user.set_password(body_json["userSend"]["newPassword"])
                user.save()
                return JsonResponse({"status": "success"}, status=OK)

            # if the password is not valid, return an custom error to prevent leak of information
            else:
                return JsonResponse(
                    {
                        "status": "failure",
                        "errors": {
                            "current": ["Le mot de passe actuel ne correspond pas"]
                        },
                    },
                )

        # if the user is not found, return an HTTP Status code not found
        except User.DoesNotExist:
            raise Http404("Student not found")


# get the cv of a user
def cvPublic(request, id):
    try:

        # get the user by id from the url parameter
        user = Student.objects.get(user=id)

        try:

            # get the cv path from the user
            cv_path = f"authentication/files/cv/public_{id}.{user.cv_path}"

            # return the cv file
            return FileResponse(open(f"{settings.BASE_DIR}/{cv_path}", "rb"))

        # if the cv is not found, return an HTTP Status code not found
        except IOError:
            return JsonResponse({"notExist": "failure"}, status=NOT_FOUND)

    # if the user is not found, return an HTTP Status code not found
    except Student.DoesNotExist:
        return JsonResponse({"notExist": "failure"}, status=NOT_FOUND)


# profile picture view
def photo(request, id):

    # if the method is PUT, update the profile picture
    if request.method == "PUT":
        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        # get the user by id from the url parameter
        user: User = User.objects.get(id=id)
        user.logo.save(f"{id}.{body_json['extensionFile']}", ContentFile(
            base64.b64decode(body_json["filePhoto"])), save=True)
        user.save()
        # return an HTTP Status code success
        return JsonResponse({"status": "success"}, status=OK)

    # if the method is GET, get the profile picture
    try:

        # get the user by id from the url parameter
        user = User.objects.get(id=id)

        try:

            # get the profile picture path from the user and return it
            path_img = user.logo.url
            return FileResponse(open(f"{settings.BASE_DIR}/{path_img}", "rb"))

        # if the profile picture is not found, return an HTTP Status code not found
        except IOError:
            return FileResponse(
                open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb")
            )

    # if the user is not found, return an HTTP Status code not found
    except User.DoesNotExist:
        raise Http404("User not found")


# get the profile picture of a school
def school_photo(request, id):

    # if the method is PUT, update the profile picture
    if request.method == "PUT":

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        # get the user by id from the url parameter
        school: School = School.objects.get(id=id)
        school.logo.save(f"{id}.{body_json['extensionFile']}", ContentFile(
            base64.b64decode(body_json["fileEntity"])), save=True)
        school.save()
        # return an HTTP Status code success
        return JsonResponse({"status": "success"}, status=OK)

    try:

        # get the school by id from the url parameter
        school = School.objects.get(id=id)

        try:
            # get the profile picture path from the school and return it
            path_img = school.logo.url
            return FileResponse(open(f"{settings.BASE_DIR}/{path_img}", "rb"))

        # if the profile picture is not found, return an HTTP Status code not found
        except IOError:
            return FileResponse(
                open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb")
            )

    # if the school is not found, return an HTTP Status code not found
    except School.DoesNotExist:
        raise Http404("School not found")


# get the profile picture of a company


def company_photo(request, id):

    # if the method is PUT, update the profile picture
    if request.method == "PUT":

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        # get the user by id from the url parameter
        company: Company = Company.objects.get(id=id)
        company.logo.save(f"{id}.{body_json['extensionFile']}", ContentFile(
            base64.b64decode(body_json["fileEntity"])), save=True)
        company.save()
        # return an HTTP Status code success
        return JsonResponse({"status": "success"}, status=OK)

    try:

        # get the company by id from the url parameter
        company = Company.objects.get(id=id)

        try:

            # get the profile picture path from the company and return it
            path_img = company.logo.url
            return FileResponse(open(f"{settings.BASE_DIR}/{path_img}", "rb"))

        # if the profile picture is not found, return an HTTP Status code not found
        except IOError:
            return FileResponse(
                open(f"{settings.BASE_DIR}/static/img/avatar.png", "rb")
            )

    # if the company is not found, return an HTTP Status code not found
    except Company.DoesNotExist:
        raise Http404("Company not found")


# forgot password view
def forgotPassword(request):

    # if the method is POST, send an email to the user with a link to reset his password
    if request.method == "POST":

        # get the body of the request
        body = request.body.decode("utf-8")
        body_json = json.loads(body)

        try:

            # get the user by email from the body
            user = User.objects.get(email=body_json["email"])

            # generate a temporary password and save it
            alphabet = string.ascii_letters + string.digits
            password = "".join(secrets.choice(alphabet) for i in range(10))
            user.set_password(password)
            user.save()

            # send an email to the user with his temporary password
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

            # return an HTTP Status code success if the email is sent
            if str(result.status_code) == "200":
                return JsonResponse({"status": "success"}, status=OK)

            # if the email is not sent, return an HTTP Status code bad request
            else:
                return JsonResponse(
                    {
                        "status": "failure",
                        "message": "Il y a eu un problème lors de l'envoie du mail",
                    },
                    status=BAD_REQUEST,
                )

        # if the user is not found, return an HTTP Status code not found
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "failure", "message": "Aucun utilisateur trouvé"},
                status=NOT_FOUND,
            )
