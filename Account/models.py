from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from datetime import timedelta
from datetime import date

class CustomUserManager(BaseUserManager):
    def create_user(self, national_id, password, **extra_fields):
        if not national_id:
            raise ValueError('The National ID field must be set')
        user = self.model(national_id=national_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, national_id, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_status', 'active')
        # Provide default values for required fields
        extra_fields.setdefault('birthday', date(1970, 1, 1))
        extra_fields.setdefault('full_name', 'Admin')
        extra_fields.setdefault('gender', 'other')
        extra_fields.setdefault('address', 'Admin Address')
        extra_fields.setdefault('user_type', 'doctor')  # or 'pharmacist' or 'patient'
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('account_status') != 'active':
            raise ValueError('Superuser must have account_status="active".')

        return self.create_user(national_id, password, **extra_fields)
    def is_otp_valid(self):
        if self.otp and self.otp_created_at:
            return timezone.now() <= self.otp_created_at + timedelta(minutes=10)
        return False
class CustomUser(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('doctor', 'Doctor'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
        ('admin', 'Admin'), 

    ]
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    national_id = models.CharField(max_length=14, unique=True, validators=[RegexValidator(r'^[0-9]{14}$')])
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_number = models.CharField(max_length=15, unique=True, validators=[RegexValidator(r'^[0-9]{10,15}$')])
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    birthday = models.DateField(null=False)
    address = models.TextField()
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    hospital = models.CharField(max_length=255, blank=True)
    clinic = models.CharField(max_length=255, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    pharmacy_name = models.CharField(max_length=255, blank=True)
    pharmacy_address = models.CharField(max_length=255, blank=True)
    diabetes = models.BooleanField(default=False, blank=True)
    heart_disease = models.BooleanField(default=False, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    other_diseases = models.TextField(blank=True)
    face_id_image = models.ImageField(upload_to='id_images/face/', null=True, blank=True)
    back_id_image = models.ImageField(upload_to='id_images/back/', null=True, blank=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'national_id'
    REQUIRED_FIELDS = ['email', 'phone_number']
    ACCOUNT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]
    account_status = models.CharField(
        max_length=10,
        choices=ACCOUNT_STATUS_CHOICES,
        default='pending'
    )
    def __str__(self):
        return self.full_name





