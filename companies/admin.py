from django.contrib import admin
from .models import Company
from .models import TouristGuideProfile, FinancialProfile, SupportProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "owner",
        "status",
        "phone",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "owner__email",
        "phone",
        "license_number",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("owner",)


@admin.register(TouristGuideProfile)
class TouristGuideProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "license_image",
    )

    search_fields = ("user__email",)

    autocomplete_fields = ("user",)


@admin.register(FinancialProfile)
class FinancialProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "financial_license_image",
    )

    search_fields = ("user__email",)

    autocomplete_fields = ("user",)


@admin.register(SupportProfile)
class SupportProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "notes",
    )

    search_fields = ("user__email",)

    autocomplete_fields = ("user",)