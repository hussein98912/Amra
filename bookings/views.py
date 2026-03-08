from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Booking
from .serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:
            return Booking.objects.all()

        if user.role == "COMPANY":
            return Booking.objects.filter(
                package__company=user.company
            )

        return Booking.objects.filter(pilgrim=user)

    def perform_create(self, serializer):

        user = self.request.user

        if user.role != "PILGRIM":
            raise PermissionDenied("Only pilgrims can book")

        package = serializer.validated_data["package"]

        seats = serializer.validated_data.get("seats", 1)

        total_price = package.price * seats

        if package.available_seats < seats:
            raise PermissionDenied("Not enough seats")

        serializer.save(
            pilgrim=user,
            total_price=total_price,
            remaining_amount=total_price,
            payment_status="UNPAID",
            status="PENDING"
        )

    # ✅ الدفع الجزئي
    @action(detail=True, methods=["POST"])
    def pay(self, request, pk=None):

        booking = self.get_object()

        if request.user != booking.pilgrim:
            return Response({"error": "Unauthorized"}, status=403)

        amount = Decimal(request.data.get("amount", 0))
        transaction_number = request.data.get("transaction_number")

        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        if booking.paid_amount + amount > booking.total_price:
            return Response({"error": "Payment exceeds total price"}, status=400)

        booking.paid_amount += amount
        booking.remaining_amount = booking.total_price - booking.paid_amount

        if booking.paid_amount == booking.total_price:
            booking.payment_status = "PAID"
        else:
            booking.payment_status = "PARTIAL"

        booking.transaction_number = transaction_number
        booking.save()

        return Response({
            "message": "Payment recorded",
            "paid_amount": booking.paid_amount,
            "remaining_amount": booking.remaining_amount
        })