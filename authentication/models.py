from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

# Create your models here.


# Replace the default User Manager with our own
class UserManager(BaseUserManager):
    use_in_migrations = True

    # Method to save user to the database
    def save_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email invalid")

        # lowercase the email
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # hash the password with the built-in set_password method from django, save the user and return it
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Method to create a user
    def create_user(self, email, password=None, **extra_fields):

        # extra field for adminisrator
        extra_fields["is_superuser"] = False
        extra_fields["is_staff"] = False

        # Call the save_user method
        return self.save_user(email, password, **extra_fields)

    # Method called while creating a staff user
    def create_staffuser(self, email, password, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = False

        # Call the save_user method
        return self.save_user(email, password, **extra_fields)

    # Method called while calling creatsuperuser
    def create_superuser(self, email, password, **extra_fields):

        # Set is_superuser parameter to true
        extra_fields.setdefault("is_superuser", True)

        # Raise an error if the user is is_superuser is not true
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser should be True")

        # Set is_staff parameter to true as well
        extra_fields["is_staff"] = True

        # Call the save_user method
        return self.save_user(email, password, **extra_fields)


# User model
class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "users"

    email = models.CharField(
        max_length=75, unique=True, validators=[EmailValidator()], verbose_name="Email"
    )
    first_name = models.CharField(max_length=75, verbose_name="First Name")
    last_name = models.CharField(max_length=75, verbose_name="Last Name")
    logo = models.ImageField(
        upload_to='authentication/files/picture', blank=True, null=True)
    extension_picture = models.CharField(
        max_length=20, default="NULL", verbose_name="Picture Extension"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # replace the default username field with email (use for login)
    USERNAME_FIELD = "email"

    # ! is necessary to import the UserManager class to use create_user, and more methods from the UserManager
    objects = UserManager()
    is_staff = models.BooleanField(default=False)  # ! is necessary
    is_active = models.BooleanField(default=True)  # ! is necessary

    # custom method to get the type of the user
    def getUserType(self):
        if self.isStudent():
            return "Student"

        elif self.isCompany():
            return "Company"

        else:
            return "School"

    # custom method to check if the user is a student and if exists
    def isStudent(student):
        try:
            studentFind = Student.objects.get(user=student)
            if studentFind:
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False

    # custom method to check if the user is a company and if exists
    def isCompany(user):
        try:
            companyFind = list(Company.objects.filter(users=user).values())
            if len(companyFind):
                return True
            else:
                return False
        except Company.DoesNotExist:
            return False


# Company model
class Company(models.Model):

    name = models.CharField(max_length=75, verbose_name="Company Name")
    description = models.TextField(
        verbose_name="Company Description", null=True)
    city = models.CharField(max_length=75, verbose_name="City", null=True)
    street = models.CharField(max_length=75, verbose_name="Street", null=True)
    logo = models.ImageField(
        upload_to='authentication/files/picture/company', blank=True, null=True)
    zip_code = models.CharField(
        max_length=75, verbose_name="Zip Code", null=True)
    extension_picture = models.CharField(
        max_length=20, default="NULL", verbose_name="Picture Extension"
    )

    # RELATIONS
    users = models.ManyToManyField(User)
    jobs = models.ManyToManyField("job.Job", related_name="company_jobs+")

    def __str__(self):
        return f"{self.name}"


class Student(models.Model):

    birthday = models.DateField(verbose_name="Birthday", null=True)
    linkedin_url = models.URLField(verbose_name="LinkedIn URL", null=True)
    cv_path = models.CharField(
        max_length=255, verbose_name="CV Path", null=True)
    description = models.TextField(verbose_name="Description", null=True)
    cv = models.FileField(
        upload_to='authentication/files/cv', blank=True, null=True)

    # RELATIONS
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class School(models.Model):

    name = models.CharField(max_length=150, verbose_name="School Name")
    description = models.TextField(
        verbose_name="School Description", null=True)
    city = models.CharField(max_length=75, verbose_name="City")
    street = models.CharField(max_length=75, verbose_name="Street")
    zip_code = models.CharField(max_length=75, verbose_name="Zip Code")
    logo = models.ImageField(
        upload_to='authentication/files/picture/school', blank=True, null=True)
    extension_picture = models.CharField(
        max_length=20, default="NULL", verbose_name="Picture Extension"
    )

    # RELATIONS
    users = models.ManyToManyField(User)
    courses = models.ManyToManyField(
        "course.Course", related_name="school_courses+")

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
