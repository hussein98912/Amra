from django.contrib import admin
from .models import User, PilgrimProfile


class PilgrimProfileInline(admin.StackedInline):
    model = PilgrimProfile
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "role",
        "status",
        "company",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    list_filter = (
        "role",
        "status",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "company__name",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("company",)

    inlines = [PilgrimProfileInline]

    readonly_fields = ("created_at",)

@admin.register(PilgrimProfile)
class PilgrimProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "phone",
        "passport_number",
    )

    search_fields = (
        "full_name",
        "passport_number",
        "phone",
    )