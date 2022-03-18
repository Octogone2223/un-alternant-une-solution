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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('description', 'name', 'city', 'street', 'zip_code')


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('description', 'name', 'city', 'street', 'zip_code')


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('description', 'birthday', 'cv_path', 'linkedin_url')
