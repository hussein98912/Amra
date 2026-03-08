from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    package_title = serializers.CharField(
        source="package.title",
        read_only=True
    )

    pilgrim_email = serializers.CharField(
        source="pilgrim.email",
        read_only=True
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "pilgrim",
            "total_price",
            "paid_amount",
            "remaining_amount",
            "payment_status",
            "status"
        ]