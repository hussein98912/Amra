from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
from .models import Ticket
from .serializers import TicketSerializer
from companies.models import Company


# -----------------------------
# Create Ticket
# -----------------------------
class CreateTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        target_type = request.data.get("target_type")
        target_company_id = request.data.get("target_company_id")

        # ✅ Role rules
        if user.role == "COMPANY":
            if target_type != "PLATFORM":
                return Response({"error": "Company can only send to platform"}, status=400)

        if user.role == "PILGRIM":
            if target_type == "COMPANY" and not target_company_id:
                return Response({"error": "Company required"}, status=400)

        # ✅ Resolve company
        target_company = None
        if target_type == "COMPANY":
            try:
                target_company = Company.objects.get(id=target_company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found"}, status=404)

        # ✅ Expiry logic
        expires_at = None

        if target_type == "PLATFORM":
            expires_at = timezone.now() + timedelta(days=2)

        elif target_type == "COMPANY":
            expires_at = timezone.now() + timedelta(days=1)

        # ✅ Create ticket
        ticket = Ticket.objects.create(
            created_by=user,
            target_type=target_type,
            target_company=target_company,
            subject=request.data.get("subject"),
            description=request.data.get("description"),
            expires_at=expires_at,  # ✅ NEW FIELD
        )

        return Response({
            "id": ticket.id,
            "expires_at": ticket.expires_at
        })


# -----------------------------
# My Tickets
# -----------------------------
class MyTicketsAPIView(ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 🟣 PLATFORM (ADMIN / SUPPORT)
        if user.role in ["ADMIN", "SUPPORT"]:
            return Ticket.objects.filter(
                target_type="PLATFORM"
            ).order_by("-created_at")

        # 🟢 COMPANY
        if user.role == "COMPANY":
            return Ticket.objects.filter(
                target_type="COMPANY",
                target_company=user.company
            ).order_by("-created_at")

        # 🔵 PILGRIM
        if user.role == "PILGRIM":
            return Ticket.objects.filter(
                created_by=user
            ).order_by("-created_at")

        return Ticket.objects.none()


# -----------------------------
# Ticket Detail
# -----------------------------
class TicketDetailAPIView(RetrieveAPIView):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]







# -----------------------------
# Update Status (Admin/Support)
# -----------------------------
class UpdateTicketStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        user = request.user

        try:
            ticket = Ticket.objects.get(id=pk)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=404)

        # 🟣 PLATFORM (ADMIN / SUPPORT)
        if user.role in ["ADMIN", "SUPPORT"]:
            if ticket.target_type != "PLATFORM":
                raise PermissionDenied("You can only update platform tickets")

        # 🟢 COMPANY
        elif user.role == "COMPANY":
            if ticket.target_type != "COMPANY" or ticket.target_company != user.company:
                raise PermissionDenied("Not your company ticket")

        # 🔵 PILGRIM
        else:
            raise PermissionDenied("Not allowed")

        # ✅ Validate status
        status_value = request.data.get("status")

        if status_value not in dict(Ticket.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)

        ticket.status = status_value
        ticket.save()

        return Response({"message": "Updated"})