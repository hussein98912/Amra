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
        user.company = company
        user.save()
        return company
    

class CompanyUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
            "name",
            "license_number",
            "phone",
            "address",
            "qr_code_image",
            "id_card_image",
        ]


class SupportUpdateSerializer(serializers.ModelSerializer):

    notes = serializers.CharField(
        source="support_profile.notes",
        required=False
    )

    class Meta:
        model = User
        fields = [
            "email",
            "notes"
        ]

    def update(self, instance, validated_data):

        profile_data = validated_data.pop("support_profile", {})

        instance.email = validated_data.get("email", instance.email)
        instance.save()

        profile = instance.support_profile

        for attr, value in profile_data.items():
            setattr(profile, attr, value)

        profile.save()

        return instance
    
class FinancialUpdateSerializer(serializers.ModelSerializer):

    financial_license_image = serializers.ImageField(
        source="financial_profile.financial_license_image",
        required=False
    )

    class Meta:
        model = User
        fields = [
            "email",
            "financial_license_image"
        ]

    def update(self, instance, validated_data):

        profile_data = validated_data.pop("financial_profile", {})

        instance.email = validated_data.get("email", instance.email)
        instance.save()

        profile = instance.financial_profile

        for attr, value in profile_data.items():
            setattr(profile, attr, value)

        profile.save()

        return instance
    


class GuideUpdateSerializer(serializers.ModelSerializer):

    license_image = serializers.ImageField(
        source="tourist_profile.license_image",
        required=False
    )

    class Meta:
        model = User
        fields = [
            "email",
            "license_image"
        ]

    def update(self, instance, validated_data):

        profile_data = validated_data.pop("tourist_profile", {})

        instance.email = validated_data.get("email", instance.email)
        instance.save()

        profile = instance.tourist_profile

        for attr, value in profile_data.items():
            setattr(profile, attr, value)

        profile.save()

        return instance
    

class CompanySerializer(serializers.ModelSerializer):

    owner_email = serializers.CharField(source="owner.email", read_only=True)

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
        ]


class EmployeeSerializer(serializers.ModelSerializer):
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
            "created_at"
        ]

class EmployeeDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    
    # Include profiles if exist
    tourist_profile = serializers.SerializerMethodField()
    financial_profile = serializers.SerializerMethodField()
    support_profile = serializers.SerializerMethodField()

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
            "tourist_profile",
            "financial_profile",
            "support_profile",
        ]

    def get_tourist_profile(self, obj):
        if hasattr(obj, "tourist_profile"):
            return {
                "license_image": obj.tourist_profile.license_image.url if obj.tourist_profile.license_image else None
            }
        return None

    def get_financial_profile(self, obj):
        if hasattr(obj, "financial_profile"):
            return {
                "financial_license_image": obj.financial_profile.financial_license_image.url if obj.financial_profile.financial_license_image else None
            }
        return None

    def get_support_profile(self, obj):
        if hasattr(obj, "support_profile"):
            return {
                "notes": obj.support_profile.notes
            }
        return None
    

class FullEmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)  # ✅ add full_name
    license_image = serializers.ImageField(required=False)
    financial_license_image = serializers.ImageField(required=False)
    notes = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "full_name",  # added here
            "email",
            "license_image",
            "financial_license_image",
            "notes",
        ]

    def validate(self, attrs):
        user = self.instance

        if user.role != "GUIDE" and "license_image" in attrs:
            raise serializers.ValidationError("Only guides can update license_image")

        if user.role != "FINANCE" and "financial_license_image" in attrs:
            raise serializers.ValidationError("Only finance can update financial_license_image")

        if user.role != "SUPPORT" and "notes" in attrs:
            raise serializers.ValidationError("Only support can update notes")

        return attrs

    def update(self, instance, validated_data):
        # ✅ تحديث full_name
        if "full_name" in validated_data:
            instance.full_name = validated_data["full_name"]

        # ✅ تحديث email (اختياري)
        if "email" in validated_data:
            instance.email = validated_data["email"]

        instance.save()

        # ✅ حسب نوع الموظف
        if instance.role == "GUIDE":
            if not hasattr(instance, "tourist_profile"):
                raise serializers.ValidationError("Tourist profile not found")

            profile = instance.tourist_profile
            if "license_image" in validated_data:
                profile.license_image = validated_data["license_image"]
            profile.save()

        elif instance.role == "FINANCE":
            if not hasattr(instance, "financial_profile"):
                raise serializers.ValidationError("Financial profile not found")

            profile = instance.financial_profile
            if "financial_license_image" in validated_data:
                profile.financial_license_image = validated_data["financial_license_image"]
            profile.save()

        elif instance.role == "SUPPORT":
            if not hasattr(instance, "support_profile"):
                raise serializers.ValidationError("Support profile not found")

            profile = instance.support_profile
            if "notes" in validated_data:
                profile.notes = validated_data["notes"]
            profile.save()

        return instance