from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,PilgrimRegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer


def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)



class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        role = request.data.get("role", "PILGRIM").upper()

        if role == "PILGRIM":
            serializer = PilgrimRegisterSerializer(data=request.data)
        else:
            serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data

            return Response({
                "message": f"{role} account created successfully",
                "user": user_data,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user info
        user_data = UserSerializer(user).data

        # Return tokens + full user info + message
        return Response({
            "message": "Login successful",
            "user": user_data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
    

class PilgrimRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PilgrimRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save user + pilgrim profile
        user = serializer.save()

        # Serialize full user data
        user_data = UserSerializer(user).data

        return Response({
            "message": "Pilgrim account created successfully",
            "user": user_data
        }, status=status.HTTP_201_CREATED)
    
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
        
