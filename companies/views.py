from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import CompanyRegisterSerializer
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import User
from users.serializers import UserSerializer


class CompanyRegisterView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the company and user
        company = serializer.save()
        user = company.owner

        # Serialize full user data (with company info)
        user_data = UserSerializer(user).data

        return Response({
            "message": "Company registered successfully. Waiting for approval.",
            "user": user_data
        }, status=status.HTTP_201_CREATED)

class CompanyStatusUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, id):

        if request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        company = Company.objects.get(id=id)

        status_value = request.data.get("status")

        if status_value not in ["PENDING","WAITING_PAYMENT","ACTIVE","REJECTED"]:
            return Response({"error": "Invalid status"}, status=400)

        company.status = status_value
        company.save()

        return Response({"message": "Status updated"})
    
class CompanyMeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        company = Company.objects.filter(
            owner=request.user
        ).first()

        if not company:
            return Response({"error": "Company not found"}, status=404)

        return Response({
            "name": company.name,
            "status": company.status,
            "phone": company.phone,
            "address": company.address,
            "qr_image": request.build_absolute_uri(
                company.qr_code_image.url
            ) if company.qr_code_image else None
        })


class CompanyUpdateMeView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        company = Company.objects.filter(
            owner=request.user
        ).first()

        if not company:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanyRegisterSerializer(
            company,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Company updated successfully"
        })


class CompanyUserCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            if request.user.role not in ["COMPANY", "ADMIN"]:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )

            email = request.data.get("email")
            password = request.data.get("password")
            role = request.data.get("role")

            if not email or not password or not role:
                return Response(
                    {"error": "Email, password and role are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if role not in ["GUIDE", "FINANCE", "SUPPORT"]:
                return Response(
                    {"error": "Invalid role"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            status_value = "PENDING" if role == "GUIDE" else "ACTIVE"

            # ✅ إنشاء المستخدم
            user = User.objects.create_user(
                email=email,
                password=password,
                role=role,
                company=request.user.company,
                status=status_value
            )

            # ⭐ إنشاء Profile حسب الدور
            if role == "GUIDE":
                TouristGuideProfile.objects.create(
                    user=user,
                    license_image=request.FILES.get("license_image")
                )

            elif role == "FINANCE":
                FinancialProfile.objects.create(
                    user=user,
                    financial_license_image=request.FILES.get("financial_license_image")
                )

            elif role == "SUPPORT":
                SupportProfile.objects.create(
                    user=user,
                    notes=request.data.get("notes", "")
                )

            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CompanyEmployeeListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role not in ["COMPANY", "ADMIN"]:
            return Response({"error": "Permission denied"}, status=403)

        users = User.objects.filter(
            company=request.user.company
        )

        result = []

        for user in users:

            profile_data = None

            # ⭐ جلب Profile حسب الدور
            if user.role == "GUIDE":
                profile_data = TouristGuideProfile.objects.filter(user=user).values().first()

            elif user.role == "FINANCE":
                profile_data = FinancialProfile.objects.filter(user=user).values().first()

            elif user.role == "SUPPORT":
                profile_data = SupportProfile.objects.filter(user=user).values().first()

            result.append({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "company": user.company.name if user.company else None,
                "profile": profile_data
            })

        return Response(result)
    
class CompanyEmployeeFilterView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        role = request.GET.get("role")

        if request.user.role not in ["COMPANY", "ADMIN"]:
            return Response({"error": "Permission denied"}, status=403)

        queryset = User.objects.filter(
            company=request.user.company
        )

        if role in ["GUIDE", "FINANCE", "SUPPORT"]:
            queryset = queryset.filter(role=role)

        data = list(queryset.values(
            "id",
            "email",
            "role",
            "status"
        ))

        return Response(data)

class CompanyEmployeeDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):

        if request.user.role not in ["COMPANY", "ADMIN"]:
            return Response({"error": "Permission denied"}, status=403)

        user = User.objects.filter(
            id=user_id,
            company=request.user.company
        ).first()

        if not user:
            return Response(
                {"error": "User not found"},
                status=404
            )

        user.delete()

        return Response({"message": "User deleted"})
    

class CompanyEmployeeUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):

        try:

            if request.user.role not in ["COMPANY", "ADMIN"]:
                return Response({"error": "Permission denied"}, status=403)

            user = User.objects.filter(
                id=user_id,
                company=request.user.company
            ).first()

            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # ⭐ تحديث كل البيانات الممكنة
            email = request.data.get("email")
            password = request.data.get("password")
            role = request.data.get("role")
            status_value = request.data.get("status")

            if email:
                user.email = email

            if password:
                user.set_password(password)

            if role and role in ["GUIDE", "FINANCE", "SUPPORT"]:
                user.role = role

            if status_value:
                user.status = status_value

            user.save()

            # ⭐ تحديث Profiles حسب الدور

            if user.role == "GUIDE":

                profile, _ = TouristGuideProfile.objects.get_or_create(user=user)

                if request.FILES.get("license_image"):
                    profile.license_image = request.FILES.get("license_image")

                profile.save()

            elif user.role == "FINANCE":

                profile, _ = FinancialProfile.objects.get_or_create(user=user)

                if request.FILES.get("financial_license_image"):
                    profile.financial_license_image = request.FILES.get(
                        "financial_license_image"
                    )

                profile.save()

            elif user.role == "SUPPORT":

                profile, _ = SupportProfile.objects.get_or_create(user=user)

                notes = request.data.get("notes")
                if notes:
                    profile.notes = notes

                profile.save()

            return Response({"message": "Employee updated successfully"})

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class EmployeeDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):

        try:

            if request.user.role not in ["COMPANY", "ADMIN"]:
                return Response({"error": "Permission denied"}, status=403)

            user = User.objects.filter(
                id=employee_id,
                company=request.user.company
            ).first()

            if not user:
                return Response(
                    {"error": "Employee not found"},
                    status=404
                )

            # ⭐ Profile data حسب الدور
            profile_data = None

            if user.role == "GUIDE":
                profile_data = TouristGuideProfile.objects.filter(
                    user=user
                ).values().first()

            elif user.role == "FINANCE":
                profile_data = FinancialProfile.objects.filter(
                    user=user
                ).values().first()

            elif user.role == "SUPPORT":
                profile_data = SupportProfile.objects.filter(
                    user=user
                ).values().first()

            response_data = {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "company": user.company.name if user.company else None,
                "profile": profile_data
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )