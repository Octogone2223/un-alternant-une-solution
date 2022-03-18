from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    # Method to save user to the database
    def save_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Invalid Email')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # Call this method for password hashing
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields['is_superuser'] = False
        extra_fields['is_staff'] = False
        return self.save_user(email, password, **extra_fields)

    # Method called while creating a staff user
    def create_staffuser(self, email, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = False

        return self.save_user(email, password, **extra_fields)

    # Method called while calling creatsuperuser
    def create_superuser(self, email, password, **extra_fields):

        # Set is_superuser parameter to true
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser should be True')

        extra_fields['is_staff'] = True

        return self.save_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "users"

    email = models.CharField(
        max_length=75,
        unique=True,
        validators=[EmailValidator()],
        verbose_name="Email"
    )

    first_name = models.CharField(max_length=75, verbose_name="First Name")
    last_name = models.CharField(max_length=75, verbose_name="Last Name")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Other required fields for authentication
    # If the user is a staff, defaults to false
    is_staff = models.BooleanField(default=False)  # ! check

    # If the user account is active or not. Defaults to True.
    # If the value is set to false, user will not be allowed to sign in.
    is_active = models.BooleanField(default=True)  # ! check

    USERNAME_FIELD = 'email'

    # Custom user manager
    objects = UserManager()  # ! check

    def getUserType(self):
        if (self.isStudent()):
            return 'Student'
        elif (self.isCompanyUsers()):
            return 'CompanyUser'
        else:
            return 'SchoolUser'

    def isStudent(student):
        try:
            studentFind = Student.objects.get(user=student)
            if studentFind:
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False


class Company(models.Model):
    class Meta:
        db_table = "company"

    name = models.CharField(max_length=75, verbose_name="Company Name")
    description = models.TextField(
        verbose_name="Company Description", null=True)
    city = models.CharField(max_length=75, verbose_name="City", null=True)
    street = models.CharField(max_length=75, verbose_name="Street", null=True)
    zip_code = models.CharField(
        max_length=75, verbose_name="Zip Code", null=True)
    user_companies = models.ManyToManyField(
        User)
    jobs = models.ManyToManyField('job.Job', related_name='company_jobs+')

    def __str__(self):
        return f'{self.name}'


class Student(models.Model):
    class Meta:
        db_table = "student"

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    birthday = models.DateField(verbose_name="Birthday", null=True)
    linkedin_url = models.URLField(verbose_name="LinkedIn URL", null=True)
    cv_path = models.CharField(
        max_length=255, verbose_name="CV Path", null=True)
    description = models.TextField(verbose_name="Description", null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class School(models.Model):
    class Meta:
        db_table = "school"

    name = models.CharField(max_length=75, verbose_name="School Name")
    city = models.CharField(max_length=75, verbose_name="City")
    street = models.CharField(max_length=75, verbose_name="Street")
    zip_code = models.CharField(max_length=75, verbose_name="Zip Code")
    users = models.ManyToManyField(User)

    def __str__(self):
        return f'{self.name}'
