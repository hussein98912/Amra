from django.db import models
from companies.models import Company


from django.db.models import Sum

class Package(models.Model):

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("CLOSED", "Closed"),
    )

    PACKAGE_TYPE_CHOICES = (
        ("family", "Family"),
        ("individual", "Individual"),
        ("vip", "VIP"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="packages"
    )

    guide = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guided_packages"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    package_type = models.CharField(
        max_length=20,
        choices=PACKAGE_TYPE_CHOICES
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.PositiveIntegerField()

    capacity = models.PositiveIntegerField()

    # الخدمات
    includes_flight = models.BooleanField(default=False)
    includes_hotel = models.BooleanField(default=False)
    includes_transportation = models.BooleanField(default=False)
    includes_meals = models.BooleanField(default=False)

    # معلومات الفندق
    hotel_name = models.CharField(max_length=255, blank=True)
    hotel_stars = models.PositiveIntegerField(null=True, blank=True)
    hotel_location = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_seats(self):
        booked = self.bookings.filter(
            status="confirmed"
        ).aggregate(total=Sum("seats"))["total"] or 0

        return self.capacity - booked

    def __str__(self):
        return f"{self.title} - {self.company.name}"