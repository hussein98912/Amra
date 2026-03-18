from django.db import models

# Create your models here.
class PlatformStaffProfile(models.Model):

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    department = models.CharField(
        max_length=50,
        choices=(
            ("SUPPORT", "Support"),
            ("FINANCE", "Finance"),
        )
    )

    job_title = models.CharField(max_length=100, blank=True)

    profile_image = models.ImageField(
        upload_to="staff/profile/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"