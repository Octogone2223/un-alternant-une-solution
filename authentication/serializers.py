from authentication.models import Company, School, Student, User
from rest_framework import serializers


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "last_name", "first_name")

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()


class UserSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CompanySignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "name",
            "description",
            "city",
            "street",
            "zip_code",
            "email",
            "password",
            "last_name",
            "first_name",
        )

    email = serializers.EmailField()
    password = serializers.CharField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("name", "description", "city", "street", "zip_code")


class SchoolSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            "name",
            "description",
            "city",
            "street",
            "zip_code",
            "email",
            "password",
            "last_name",
            "first_name",
        )

    email = serializers.EmailField()
    password = serializers.CharField()
    last_name = serializers.CharField()
    first_name = serializers.CharField()

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value


class SchoolSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    city = serializers.CharField()
    street = serializers.CharField()
    zip_code = serializers.CharField()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("description", "birthday", "cv_path", "linkedin_url")
