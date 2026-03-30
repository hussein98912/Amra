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
from packages.models import Package
from packages.serializers import PackageStatusUpdateSerializer
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class PilgrimViewSet(ReadOnlyModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    queryset = User.objects.filter(role="PILGRIM")
    ordering = ["-created_at"]


class CompanyViewSet(ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUser]

    # Filter only companies that have a user role of COMPANY
    queryset = Company.objects.all()
    ordering = ["-created_at"]


class AdminBookingViewSet(ReadOnlyModelViewSet):

    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]

    queryset = Booking.objects.all().order_by("-created_at")
    ordering = ["-created_at"]

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
    

class PackageStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]  # only superusers

    def post(self, request, package_id):
        try:
            package = Package.objects.get(id=package_id)
        except Package.DoesNotExist:
            return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PackageStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["status"]
        reason = serializer.validated_data.get("reason", "")

        # Update package
        package.status = status_value
        if status_value == "CLOSED":
            package.reject_reason = reason
        package.save()

        # Send notification to company owner
        if status_value == "ACTIVE":
            message = f"Your package '{package.title}' has been approved."
        else:
            message = f"Your package '{package.title}' was rejected. Reason: {reason}"

        Notification.objects.create(user=package.company.owner, message=message)

        return Response({
            "message": f"Package {status_value.lower()} successfully.",
            "package_id": package.id
        }, status=status.HTTP_200_OK)
    

class CreatePlatformStaffView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = PlatformStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Platform employee created successfully",
                "user_id": user.id
            },
            status=status.HTTP_201_CREATED
        )
    

class ManagePlatformStaffView(APIView):

    permission_classes = [IsAdminUser]

    def put(self, request, staff_id):
        try:
            user = User.objects.get(id=staff_id)
            profile = user.staff_profile
        except User.DoesNotExist:
            return Response(
                {"error": "Staff not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update user fields
        user.email = request.data.get("email", user.email)
        user.role = request.data.get("role", user.role)

        if "is_active" in request.data:
            user.is_active = request.data["is_active"]

        user.save()

        # Update profile fields
        profile.first_name = request.data.get("first_name", profile.first_name)
        profile.last_name = request.data.get("last_name", profile.last_name)
        profile.phone = request.data.get("phone", profile.phone)
        profile.job_title = request.data.get("job_title", profile.job_title)

        profile.save()

        return Response({
            "message": "Platform staff updated successfully",
            "is_active": user.is_active
        })


    def delete(self, request, staff_id):

        try:
            user = User.objects.get(id=staff_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Staff not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.role not in ["SUPPORT", "FINANCE"]:
            return Response(
                {"error": "You can only delete platform staff"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()

        return Response(
            {"message": "Platform staff deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class FinanceEmployeesView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PlatformStaffReadSerializer

    def get_queryset(self):
        return User.objects.filter(role="FINANCE", company=None)
    

class SupportEmployeesView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PlatformStaffReadSerializer

    def get_queryset(self):
        return User.objects.filter(role="SUPPORT", company=None)
    


class SuperuserInfoAPIView(APIView):
    """
    Returns the logged-in superuser info along with JWT tokens.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_superuser:
            raise PermissionDenied("You must be a superuser to access this endpoint.")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        serializer = SuperuserInfoSerializer(user)

        return Response({
            "user": serializer.data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(access)
            }
        })
    


class AdminUserStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):

        # 🔒 Only staff or superadmin
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin can update user status"},
                status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🚨 Prevent admin from disabling himself (optional but recommended)
        if user == request.user and request.data.get("status") == "REJECTED":
            return Response(
                {"error": "You cannot reject yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserStatusUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "User status updated successfully",
            "user_id": user.id,
            "new_status": user.status
        })