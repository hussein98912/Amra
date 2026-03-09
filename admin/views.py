from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from bookings.serializers import BookingSerializer
from bookings.models import Booking


User = get_user_model()


class PilgrimViewSet(ReadOnlyModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    queryset = User.objects.filter(role="PILGRIM")


class CompanyUsersViewSet(ReadOnlyModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    queryset = User.objects.filter(role="COMPANY")


class AdminBookingViewSet(ReadOnlyModelViewSet):

    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]

    queryset = Booking.objects.all().order_by("-created_at")