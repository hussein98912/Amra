from django.db import models
from django.utils import timezone
from datetime import timedelta


class Ticket(models.Model):

    TARGET_TYPE_CHOICES = (
        ("PLATFORM", "Platform"),
        ("COMPANY", "Company"),
    )

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("CLOSED", "Closed"),
    )

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="created_tickets"
    )

    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)

    target_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tickets"
    )

    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def __str__(self):
        return f"Ticket #{self.id}"


