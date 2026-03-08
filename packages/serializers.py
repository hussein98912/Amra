from rest_framework import serializers
from .models import Package


class PackageSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    guide_email = serializers.CharField(
        source="guide.email",
        read_only=True
    )

    available_seats = serializers.ReadOnlyField()

    class Meta:
        model = Package
        fields = "__all__"
        read_only_fields = ["company"]

    def create(self, validated_data):

        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError("Request context is required")

        # حفظ الشركة تلقائياً من المستخدم الحالي
        validated_data["company"] = request.user.company

        return super().create(validated_data)

    def validate(self, data):

        request = self.context["request"]
        user = request.user

        if not (user.is_superuser or user.role == "COMPANY"):
            raise serializers.ValidationError(
                "Only company can create package"
            )

        return data
        