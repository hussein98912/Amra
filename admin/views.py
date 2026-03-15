from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from bookings.serializers import BookingSerializer
from bookings.models import Booking
from companies.serializers import EmployeeSerializer,EmployeeDetailSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from companies.models import Company
from .serializers import *
from rest_framework import status
from notifications.models import Notification


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

class AdminCompanyEmployeesView(ReadOnlyModelViewSet):
    queryset = User.objects.filter(role__in=["GUIDE", "FINANCE", "SUPPORT", "COMPANY"])
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]


class AdminEmployeeDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        employee = get_object_or_404(User, id=id)
        serializer = EmployeeDetailSerializer(employee)
        return Response({
            "message": "Employee retrieved successfully",
            "employee": serializer.data
        })
    

class AdminCompanyDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        company = get_object_or_404(Company, id=id)
        serializer = CompanyDetailSerializer(company)
        return Response({
            "message": "Company retrieved successfully",
            "company": serializer.data
        })
    

class AdminPilgrimDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        pilgrim = get_object_or_404(User, id=id, role="PILGRIM")
        serializer = PilgrimDetailSerializer(pilgrim)
        return Response({
            "message": "Pilgrim retrieved successfully",
            "pilgrim": serializer.data
        })


class CompanyApproveRejectView(APIView):
    permission_classes = [IsAdminUser]  

    def post(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update company status
        company.status = data["status"]
        if data["status"] == "REJECTED":
            company.rejection_reason = data["rejection_reason"]
        else:
            company.rejection_reason = ""
        company.save()

        # Create notification for the company owner
        if company.status == "REJECTED":
            message = f"Your company '{company.name}' has been REJECTED. Reason: {company.rejection_reason}"
        else:  # APPROVED / ACTIVE
            message = f"Your company '{company.name}' has been APPROVED and is now ACTIVE."

        Notification.objects.create(
            user=company.owner,
            message=message
        )

        return Response({
            "message": f"Company {company.status} successfully.",
            "company_id": company.id,
            "status": company.status
        }, status=status.HTTP_200_OK)