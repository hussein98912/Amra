from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.db import transaction
from bookings.models import Booking
from companies.models import Company

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data

    def to_representation(self, instance):
        """
        Customize the response after validation.
        Returns a message and the full serialized user info.
        """
        user = instance.get("user")
        return {
            "message": "Login successful",
            "user": UserSerializer(user).data
        }
    

from rest_framework import serializers
from .models import User, PilgrimProfile


class PilgrimRegisterSerializer(serializers.Serializer):

    # User
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # Profile
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    phone = serializers.CharField()
    passport_number = serializers.CharField()
    nationality = serializers.ChoiceField(choices=PilgrimProfile.NATIONALITY_CHOICES)
    date_of_birth = serializers.DateField()
    emergency_contact = serializers.CharField()

    profile_image = serializers.ImageField(required=False)
    passport_image = serializers.ImageField(required=False)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        with transaction.atomic():

            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                role="PILGRIM"
            )

            PilgrimProfile.objects.create(
                user=user,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                full_name=validated_data["full_name"],
                phone=validated_data["phone"],
                passport_number=validated_data["passport_number"],
                nationality=validated_data["nationality"],
                date_of_birth=validated_data["date_of_birth"],
                emergency_contact=validated_data["emergency_contact"],
                profile_image=validated_data.get("profile_image"),
                passport_image=validated_data.get("passport_image"),
            )

        return user
    

class PilgrimProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = PilgrimProfile
        fields = [
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "passport_number",
            "nationality",
            "date_of_birth",
            "emergency_contact",
            "profile_image",
            "passport_image",
            "created_at"
        ]


class UserSerializer(serializers.ModelSerializer):

    pilgrim_profile = PilgrimProfileSerializer(read_only=True)

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

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
            "pilgrim_profile"
        ]



class UserUpdateSerializer(serializers.ModelSerializer):

    # حقول PilgrimProfile
    first_name = serializers.CharField(source="pilgrim_profile.first_name", required=False)
    last_name = serializers.CharField(source="pilgrim_profile.last_name", required=False)
    full_name = serializers.CharField(source="pilgrim_profile.full_name", required=False)
    phone = serializers.CharField(source="pilgrim_profile.phone", required=False)
    passport_number = serializers.CharField(source="pilgrim_profile.passport_number", required=False)
    emergency_contact = serializers.CharField(source="pilgrim_profile.emergency_contact", required=False)

    # الصور
    profile_image = serializers.ImageField(source="pilgrim_profile.profile_image", required=False)
    passport_image = serializers.ImageField(source="pilgrim_profile.passport_image", required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "passport_number",
            "emergency_contact",
            "profile_image",
            "passport_image",
        ]

    def update(self, instance, validated_data):

        profile_data = validated_data.pop("pilgrim_profile", {})

        # تحديث معلومات المستخدم
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # تحديث معلومات البروفايل
        profile = getattr(instance, "pilgrim_profile", None)

        if profile:
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
    

class UpcomingTripSerializer(serializers.ModelSerializer):

    package_name = serializers.CharField(source="package.title")
    hotel_name = serializers.CharField(source="package.hotel_name")
    start_date= serializers.DateField(source="package.start_date")

    class Meta:
        model = Booking
        fields = [
            "id",
            "package_name",
            "hotel_name",
            "start_date"
        ]