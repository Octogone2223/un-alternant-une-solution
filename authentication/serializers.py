from dataclasses import field
from django.http import HttpResponseBadRequest
from authentication.models import Student, User
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

    name = serializers.CharField()
    description = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()

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


class SchoolSignUpSerializer(serializers.Serializer):

    name = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()
    description = serializers.CharField()

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


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('description', 'birthday', 'cv_path', 'linkedin_url')
