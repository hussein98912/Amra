from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Booking
from .serializers import BookingSerializer
from notifications.models import Notification



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

    # -------------------------
    # إنشاء حجز
    # -------------------------

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

    # -------------------------
    # الدفع (جزئي أو كامل)
    # -------------------------

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

    # -------------------------
    # قبول الحجز من الشركة
    # -------------------------

    @action(detail=True, methods=["POST"])
    def approve(self, request, pk=None):

        booking = self.get_object()
        user = request.user

        if user.role != "COMPANY":
            return Response(
                {"error": "Only company can approve bookings"},
                status=403
            )

        if booking.package.company != user.company:
            return Response(
                {"error": "This booking does not belong to your company"},
                status=403
            )

        if booking.payment_status != "PAID":
            return Response(
                {"error": "Payment must be completed before approval"},
                status=400
            )

        booking.status = "CONFIRMED"
        booking.save()

        Notification.objects.create(
            user=booking.pilgrim,
            message=f"Your booking for {booking.package.title} has been approved"
        )

        return Response({
            "message": "Booking approved successfully"
        })

    # -------------------------
    # رفض الحجز
    # -------------------------

    @action(detail=True, methods=["POST"])
    def reject(self, request, pk=None):

        booking = self.get_object()
        user = request.user

        if user.role != "COMPANY":
            return Response(
                {"error": "Only company can reject bookings"},
                status=403
            )

        if booking.package.company != user.company:
            return Response(
                {"error": "This booking does not belong to your company"},
                status=403
            )

        reason = request.data.get("reason")

        if not reason:
            return Response(
                {"error": "Rejection reason is required"},
                status=400
            )

        booking.status = "CANCELLED"
        booking.rejection_reason = reason
        booking.save()

        Notification.objects.create(
            user=booking.pilgrim,
            message=f"Booking rejected. Reason: {reason}"
        )

        return Response({
            "message": "Booking rejected successfully"
        })
    
    
