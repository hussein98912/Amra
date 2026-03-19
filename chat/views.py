from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from.serializers import *
from .models import ChatRoom, RoomParticipant
from users.models import User
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from packages.models import Package
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count

class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        other_user_id = request.data.get("user_id")

        other_user = User.objects.get(id=other_user_id)

        # ✅ Find existing PRIVATE room with exactly these 2 users
        room = (
            ChatRoom.objects
            .filter(room_type="PRIVATE")
            .annotate(
                participant_count=Count("participants", distinct=True)
            )
            .filter(participant_count=2)
            .filter(participants=user)
            .filter(participants=other_user)
            .first()
        )

        if room:
            return Response({
                "room_id": room.id,
                "created": False
            })

        # ✅ Create new room
        room = ChatRoom.objects.create(
            created_by=user,
            room_type="PRIVATE"
        )

        room.participants.add(user, other_user)

        return Response({
            "room_id": room.id,
            "created": True
        })
    
class UserChatRooms(ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all rooms where the user is a participant
        return ChatRoom.objects.filter(participants=user).order_by("-created_at")

class MessagePagination(PageNumberPagination):

    page_size = 20


class RoomMessages(ListAPIView):

    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):

        room_id = self.kwargs["room_id"]

        return Message.objects.filter(
            room_id=room_id
        ).order_by("-created_at")


class CreateGroupChat(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        name = request.data.get("name")
        users = request.data.get("users", [])

        room = ChatRoom.objects.create(
            name=name,
            room_type="GROUP",
            created_by=request.user
        )

        RoomParticipant.objects.create(
            user=request.user,
            room=room,
            role="ADMIN"
        )

        for uid in users:

            user = User.objects.get(id=uid)

            RoomParticipant.objects.create(
                user=user,
                room=room
            )

        return Response({
            "room_id": room.id,
            "message": "Group created"
        })
    
class AddUserToGroup(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):

        user_id = request.data.get("user_id")

        user = User.objects.get(id=user_id)

        RoomParticipant.objects.create(
            user=user,
            room_id=room_id
        )

        return Response({"message": "User added"})
    
class RemoveUserFromGroup(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, user_id):

        RoomParticipant.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).delete()

        return Response({"message": "User removed"})
    

class MarkRoomAsSeen(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user
        room = ChatRoom.objects.get(id=room_id)

        # Add this user to seen_by for all messages not yet seen
        unseen_messages = Message.objects.filter(room=room).exclude(seen_by=user)
        for msg in unseen_messages:
            msg.seen_by.add(user)

        return Response({"message": "Room marked as read", "count": unseen_messages.count()})
    

class UserChatRoomsWithUnread(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rooms = ChatRoom.objects.filter(participants=user).order_by("-created_at")
        data = []

        for room in rooms:
            unread_count = Message.objects.filter(
                room=room
            ).exclude(seen_by=user).count()

            data.append({
                "room_id": room.id,
                "room_name": room.name or "Private Chat",
                "unread_messages": unread_count
            })

        return Response(data)   
    

class SupportListAPIView(generics.ListAPIView):
    """
    API endpoint to get all Support staff for all companies for the logged-in Pilgrim.
    """
    serializer_class = SupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # نفترض أن المعتمر يريد جميع موظفي الدعم لكل الشركات
        return SupportProfile.objects.filter(user__role="SUPPORT")
    


class PilgrimPackagesAPIView(generics.ListAPIView):
    """
    API endpoint to get all packages of the logged-in pilgrim
    with guide and support staff of the package's company.
    """
    serializer_class = PackageWithGuideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # نفترض أن المعتمر مرتبط بالـ Packages عبر Booking أو حسب تصميمك
        # إذا لا يوجد Booking، يمكن فلترة حسب شركته أو أي علاقة
        user = self.request.user
        if hasattr(user, "pilgrim_profile"):
            # مثال: إرجاع كل الـ Packages المرتبطة بالشركة التي ينتمي لها
            return Package.objects.filter(company=user.company, status="ACTIVE")
        return Package.objects.none()
    

class CompanyPilgrimsAPIView(generics.ListAPIView):
    """
    API endpoint to return all pilgrims who booked packages of the logged-in company
    """
    serializer_class = PilgrimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Ensure the user is a company owner
        if user.role != "COMPANY" or not user.company:
            return User.objects.none()

        # Get all confirmed bookings for packages of this company
        return User.objects.filter(
            bookings__package__company=user.company,
            bookings__status="CONFIRMED"
        ).distinct()
    

class CompanyEmployeesAPIView(generics.ListAPIView):
    """
    API endpoint to get all employees of the logged-in company
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Only allow company owners to see their employees
        if user.role != "COMPANY" or not user.company:
            return User.objects.none()

        # Return all users within the same company
        return User.objects.filter(company=user.company)
    

class PlatformEmployeesAPIView(generics.ListAPIView):
    """
    API endpoint to get all platform employees.
    Only accessible if the logged-in user is:
    - a platform staff (has staff_profile)
    OR
    - a superuser
    """
    serializer_class = PlatformStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Allow access only if staff or superuser
        if not (hasattr(user, "staff_profile") or user.is_superuser):
            raise PermissionDenied("You must be a staff member or superuser to access this API.")

        # Return all platform staff
        return PlatformStaffProfile.objects.all().order_by("department", "first_name")