from rest_framework import serializers
from .models import Company
from users.models import User

class CompanyRegisterSerializer(serializers.Serializer):

    # بيانات المستخدم
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # بيانات الشركة
    name = serializers.CharField()
    license_number = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField()
    address = serializers.CharField()

    # الصور
    qr_code_image = serializers.ImageField(required=False)
    id_card_image = serializers.ImageField(required=False)

    def create(self, validated_data):

        qr_image = validated_data.pop("qr_code_image", None)
        id_image = validated_data.pop("id_card_image", None)

        # إنشاء المستخدم
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role="COMPANY"
        )

        # منع إنشاء أكثر من شركة لنفس المستخدم
        if Company.objects.filter(owner=user).exists():
            raise serializers.ValidationError("You already own a company")

        # إنشاء الشركة
        company = Company.objects.create(
            owner=user,
            name=validated_data["name"],
            license_number=validated_data.get("license_number"),
            phone=validated_data["phone"],
            address=validated_data["address"],
            qr_code_image=qr_image,
            id_card_image=id_image,
            status="PENDING"
        )

        return company