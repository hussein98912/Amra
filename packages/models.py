from django.db import models
from companies.models import Company

class Package(models.Model):

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("CLOSED", "Closed"),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="packages")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField()

    capacity = models.IntegerField()
    available_seats = models.IntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")

    def __str__(self):
        return self.title