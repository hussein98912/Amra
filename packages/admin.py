from django.contrib import admin
from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "company",
        "package_type",
        "price",
        "capacity",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "package_type",
        "created_at",
        "company",
    )

    search_fields = (
        "title",
        "description",
        "hotel_name",
        "company__name",
    )

    ordering = ("-created_at",)

    autocomplete_fields = (
        "company",
        "guide",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )