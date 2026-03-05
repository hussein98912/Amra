from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import CompanyRegisterSerializer
from .models import Company
from rest_framework.parsers import MultiPartParser, FormParser


class CompanyRegisterView(APIView):

    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):

        serializer = CompanyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Company registered successfully. Waiting for approval."
        })

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