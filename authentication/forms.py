from dataclasses import field
from django.http import HttpResponseBadRequest
from authentication.models import Company, School, Student, User
from rest_framework import serializers


class UserSignUpSerializer(serializers.Serializer):
    class Meta:
        model = User

    email = serializers.EmailField()
    password = serializers.CharField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()

    def __check_email__(self, value):
        email = value.get('email').lower()

        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise serializers.ValidationError({'email': 'Email already exists'})


class UserSignInSerializer(serializers.Serializer):
    class Meta:
        model = User

    email = serializers.EmailField()
    password = serializers.CharField()


class CompanySignUpSerializer(serializers.Serializer):
    class Meta:
        model = Company

    name = serializers.CharField()
    description = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()


class SchoolSignUpSerializer(serializers.Serializer):
    class Meta:
        model = School

    name = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()
