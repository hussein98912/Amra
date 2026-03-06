from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="PILGRIM", **extra):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password, role="ADMIN")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("COMPANY", "Company Owner"),
        ("GUIDE", "Guide"),
        ("FINANCE", "Finance"),
        ("SUPPORT", "Support"),
        ("PILGRIM", "Pilgrim"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("REJECTED", "Rejected"),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    


class PilgrimProfile(models.Model):

    NATIONALITY_CHOICES = (
        ("SYRIAN", "Syrian"),
        ("SYRIAN_PALESTINIAN", "Syrian Palestinian"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pilgrim_profile"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)
    passport_number = models.CharField(max_length=50)

    nationality = models.CharField(max_length=30, choices=NATIONALITY_CHOICES)

    date_of_birth = models.DateField()
    emergency_contact = models.CharField(max_length=20)

    profile_image = models.ImageField(upload_to="pilgrims/profile/", null=True, blank=True)
    passport_image = models.ImageField(upload_to="pilgrims/passports/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name