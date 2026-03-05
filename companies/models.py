from django.db import models
from django.conf import settings

class Company(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("WAITING_PAYMENT", "Waiting Payment"),
        ("ACTIVE", "Active"),
        ("REJECTED", "Rejected"),
    )

    owner = models.CharField(max_length=255)

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