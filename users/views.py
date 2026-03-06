from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,PilgrimRegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import User

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User created"}, status=201)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        from django.contrib.auth import authenticate
        user = authenticate(
            email=request.data.get("email"),
            password=request.data.get("password"),
        )
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
    
class PilgrimRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PilgrimRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Pilgrim account created"}, status=201)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get("refresh")

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully"})

        except Exception:
            return Response({"error": "Invalid token"}, status=400)
        
class ApproveUserView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):

        try:

            if not request.user.is_superuser:
                return Response(
                    {"error": "Only admin can approve users"},
                    status=status.HTTP_403_FORBIDDEN
                )

            user = User.objects.filter(id=user_id).first()

            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if user.role == "GUIDE":
                user.status = "ACTIVE"

            elif user.role in ["FINANCE", "SUPPORT"]:
                user.status = "ACTIVE"

            user.save()

            return Response(
                {"message": "User approved"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
