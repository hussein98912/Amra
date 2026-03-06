from django.db import models
from django.conf import settings

class Company(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("WAITING_PAYMENT", "Waiting Payment"),
        ("ACTIVE", "Active"),
        ("REJECTED", "Rejected"),
    )

    owner = models.ForeignKey(
                    "users.User",
                    on_delete=models.CASCADE,
                    related_name="companies"
                    )

    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100,blank=True,null=True)

    phone = models.CharField(max_length=50)
    address = models.TextField()

    qr_code_image = models.ImageField(upload_to="company/qr/",blank=True,null=True)
    id_card_image = models.ImageField(upload_to="company/docs/",blank=True,null=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)


class TouristGuideProfile(models.Model):

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="tourist_profile"
    )

    license_image = models.ImageField(upload_to="guide/license/")



class FinancialProfile(models.Model):

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="financial_profile"
    )

    financial_license_image = models.ImageField(upload_to="finance/license/")


class SupportProfile(models.Model):

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="support_profile"
    )

    notes = models.TextField(blank=True)