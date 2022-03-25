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

    extension_picture = models.CharField(
        max_length=20, default='NULL', verbose_name="Picture Extension")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    # ! is necessary to import the UserManager class like create_user method
    objects = UserManager()

    is_staff = models.BooleanField(default=False)  # ! is necessary
    is_active = models.BooleanField(default=True)  # ! is necessary

    def getUserType(self):
        if (self.isStudent()):
            return 'Student'
        elif (self.isCompany()):
            return 'Company'
        else:
            return 'School'

    def isStudent(student):
        try:
            studentFind = Student.objects.get(user=student)
            if studentFind:
                return True
            else:
                return False
        except Student.DoesNotExist:
            return False

    def isCompany(user):
        try:
            companyFind = list(Company.objects.filter(
                users=user).values())
            if len(companyFind):
                return True
            else:
                return False
        except Company.DoesNotExist:
            print("dd")
            return False


class Company(models.Model):

    name = models.CharField(max_length=75, verbose_name="Company Name")
    description = models.TextField(
        verbose_name="Company Description", null=True)
    city = models.CharField(max_length=75, verbose_name="City", null=True)
    street = models.CharField(max_length=75, verbose_name="Street", null=True)
    zip_code = models.CharField(
        max_length=75, verbose_name="Zip Code", null=True)
    extension_picture = models.CharField(
        max_length=20, default='NULL', verbose_name="Picture Extension")
    users = models.ManyToManyField(
        User)
    jobs = models.ManyToManyField('job.Job', related_name='company_jobs+')

    def __str__(self):
        return f'{self.name}'


class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    birthday = models.DateField(verbose_name="Birthday", null=True)
    linkedin_url = models.URLField(verbose_name="LinkedIn URL", null=True)
    cv_path = models.CharField(
        max_length=255, verbose_name="CV Path", null=True)
    description = models.TextField(verbose_name="Description", null=True)
    course = models.ForeignKey(
        'course.Course', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class School(models.Model):

    name = models.CharField(max_length=150, verbose_name="School Name")
    description = models.TextField(
        verbose_name="School Description", null=True)
    city = models.CharField(max_length=75, verbose_name="City")
    street = models.CharField(max_length=75, verbose_name="Street")
    zip_code = models.CharField(max_length=75, verbose_name="Zip Code")

    extension_picture = models.CharField(
        max_length=20, default='NULL', verbose_name="Picture Extension")
    users = models.ManyToManyField(User)
    courses = models.ManyToManyField(
        'course.Course', related_name='school_courses+')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
