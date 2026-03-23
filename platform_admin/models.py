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
    


# class CompanySubscription(models.Model):

#     name = models.CharField(max_length=100)  # مثال: Basic / Premium

#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     duration_days = models.IntegerField()  # مثلا 30 يوم

#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)


# class CompanyPayment(models.Model):

#     STATUS_CHOICES = (
#         ("PENDING", "Pending"),
#         ("APPROVED", "Approved"),
#         ("REJECTED", "Rejected"),
#     )

#     company = models.ForeignKey(
#         "companies.Company",
#         on_delete=models.CASCADE,
#         related_name="payments"
#     )

#     subscription = models.ForeignKey(   # ✅ بدل amount المباشر
#         CompanySubscription,
#         on_delete=models.SET_NULL,
#         null=True
#     )

#     transaction_id = models.CharField(max_length=255)

#     payment_proof = models.ImageField(upload_to="payments/proofs/")

#     # ✅ optional: نخزن السعر وقت الدفع (snapshot)
#     amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

#     reviewed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)

#     reason = models.TextField(blank=True, null=True)

#     created_at = models.DateTimeField(auto_now_add=True)