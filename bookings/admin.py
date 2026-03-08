from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "pilgrim",
        "package",
        "status",
        "payment_status",
        "total_price",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "pilgrim__email",
        "package__title",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("pilgrim", "package")

    readonly_fields = ("created_at",)