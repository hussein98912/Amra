from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data
    

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