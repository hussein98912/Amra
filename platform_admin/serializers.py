from rest_framework import serializers
from users.models import User
from companies.models import Company
from companies.serializers import EmployeeDetailSerializer
from .models import *

class CompanyDetailSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    
    # Include employees of this company
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "owner",
            "owner_email",
            "name",
            "license_number",
            "phone",
            "address",
            "qr_code_image",
            "id_card_image",
            "status",
            "created_at",
            "employees",
        ]

    def get_employees(self, obj):
        # Return all users of the company with full details
        users = User.objects.filter(company=obj)
        serializer = EmployeeDetailSerializer(users, many=True)
        return serializer.data
    


class PilgrimDetailSerializer(serializers.ModelSerializer):
    pilgrim_profile = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "status",
            "company",
            "company_name",
            "is_active",
            "is_staff",
            "created_at",
            "pilgrim_profile",
        ]

    def get_pilgrim_profile(self, obj):
        profile = getattr(obj, "pilgrim_profile", None)
        if profile:
            return {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "full_name": profile.full_name,
                "phone": profile.phone,
                "passport_number": profile.passport_number,
                "nationality": profile.nationality,
                "date_of_birth": profile.date_of_birth,
                "emergency_contact": profile.emergency_contact,
                "profile_image": profile.profile_image.url if profile.profile_image else None,
                "passport_image": profile.passport_image.url if profile.passport_image else None,
                "created_at": profile.created_at,
            }
        return None
    

class CompanyApprovalSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[("ACTIVE", "Active"), ("REJECTED", "Rejected")])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["status"] == "REJECTED" and not data.get("rejection_reason"):
            raise serializers.ValidationError("Rejection reason is required when rejecting a company.")
        return data
    


class CompanySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "license_number",
            "phone",
            "address",
            "status",
            "created_at",
            "owner_email",
        ]


class PlatformStaffSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    phone = serializers.CharField()

    role = serializers.ChoiceField(
        choices=["SUPPORT", "FINANCE"]
    )

    job_title = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):

        role = validated_data["role"]

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=role
        )

        user.status = "ACTIVE"
        user.is_staff = True
        user.company = None
        user.save()

        PlatformStaffProfile.objects.create(
            user=user,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            department=role,
            job_title=validated_data.get("job_title", "")
        )

        return user
    

class PlatformStaffReadSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="staff_profile.first_name", read_only=True)
    last_name = serializers.CharField(source="staff_profile.last_name", read_only=True)
    phone = serializers.CharField(source="staff_profile.phone", read_only=True)
    job_title = serializers.CharField(source="staff_profile.job_title", read_only=True)
    department = serializers.CharField(source="staff_profile.department", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "first_name",
            "last_name",
            "phone",
            "job_title",
            "department"
        ]


class SuperuserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "is_superuser", "is_staff", "created_at"]