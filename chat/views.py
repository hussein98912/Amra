from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    ChatRoomWithMetaSerializer,
    MessageSerializer,
    RoomDetailSerializer,
    SupportSerializer,
    PackageWithGuideSerializer,
    PilgrimSerializer,
    EmployeeSerializer,
    PlatformStaffSerializer,
)
from .models import ChatRoom, RoomParticipant, Message
from users.models import User
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from packages.models import Package
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Q, OuterRef, Subquery, F
from companies.models import SupportProfile
from platform_admin.models import PlatformStaffProfile
from companies.models import Company


class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        other_user_id = request.data.get("user_id")

        # ✅ Fix #6 - validate user_id exists in request
        if not other_user_id:
            return Response({"error": "user_id is required"}, status=400)

        # ✅ Prevent self-chat
        if str(other_user_id) == str(user.id):
            return Response({"error": "Cannot create a room with yourself"}, status=400)

        # ✅ Fix #3 - handle user not found
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

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
        }, status=201)


class UserChatRooms(ListAPIView):
    serializer_class = ChatRoomWithMetaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        last_message_subquery = Message.objects.filter(
            room=OuterRef("pk")
        ).order_by("-created_at")

        return (
            ChatRoom.objects
            .filter(participants=user)
            .filter(roomparticipant__user=user)
            .annotate(
                unread_count=Count(
                    "messages",
                    filter=(
                        (
                            Q(messages__id__gt=F("roomparticipant__last_seen_message")) |
                            Q(roomparticipant__last_seen_message__isnull=True)
                        )
                        & ~Q(messages__sender=user)
                    )
                ),
                last_message_text=Subquery(
                    last_message_subquery.values("text")[:1]
                ),
                last_message_time=Subquery(
                    last_message_subquery.values("created_at")[:1]
                ),
                last_message_sender=Subquery(
                    last_message_subquery.values("sender__email")[:1]
                ),
            )
            .prefetch_related("participants")
            .order_by("-last_message_time", "-created_at")
        )


class MessagePagination(PageNumberPagination):
    page_size = 20


class RoomMessages(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]  # ✅ Fix - was missing

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        user = self.request.user

        # ✅ Fix #1 - check user is a participant
        if not ChatRoom.objects.filter(id=room_id, participants=user).exists():
            raise PermissionDenied("You are not part of this room")

        return (
            Message.objects
            .filter(room_id=room_id)
            .prefetch_related("seen_by")  # ✅ Fix #11 - avoid N+1 on seen_by
            .order_by("-created_at")
        )


class CreateGroupChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        users = request.data.get("users", [])

        # ✅ Fix #15 - validate group name
        if not name or not name.strip():
            return Response({"error": "Group name is required"}, status=400)

        room = ChatRoom.objects.create(
            name=name.strip(),
            room_type="GROUP",
            created_by=request.user
        )

        RoomParticipant.objects.create(
            user=request.user,
            room=room,
            role="ADMIN"
        )

        for uid in users:
            # ✅ Fix #3 - handle user not found in loop
            try:
                user = User.objects.get(id=uid)
            except User.DoesNotExist:
                continue  # skip invalid users silently, or return error if you prefer

            RoomParticipant.objects.create(
                user=user,
                room=room
            )

        return Response({
            "room_id": room.id,
            "message": "Group created"
        }, status=201)


class AddUserToGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user
        user_id = request.data.get("user_id")

        # ✅ Validate user_id
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        # ✅ Check if requester is ADMIN
        if not RoomParticipant.objects.filter(
            room_id=room_id,
            user=user,
            role="ADMIN"
        ).exists():
            raise PermissionDenied("Only admins can add users")

        # ✅ Check if user already exists in group
        if RoomParticipant.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).exists():
            return Response({"message": "User already in group"})

        # ✅ Fix #3 - handle user not found
        try:
            new_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        RoomParticipant.objects.create(
            user=new_user,
            room_id=room_id
        )

        return Response({"message": "User added"}, status=201)


class RemoveUserFromGroup(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        user = request.user
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        # ✅ Only admin can remove
        if not RoomParticipant.objects.filter(
            room_id=room_id,
            user=user,
            role="ADMIN"
        ).exists():
            raise PermissionDenied("Only admins can remove users")

        # ✅ Fix #14 - prevent removing another admin
        target = RoomParticipant.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).first()

        if not target:
            return Response({"error": "User not in group"}, status=404)

        if target.role == "ADMIN":
            return Response({"error": "Cannot remove an admin from the group"}, status=400)

        target.delete()

        return Response({"message": "User removed"})


class MarkRoomAsSeen(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user
        last_message_id = request.data.get("last_message_id")

        if not last_message_id:
            return Response({"error": "last_message_id required"}, status=400)

        try:
            message = Message.objects.get(id=last_message_id, room_id=room_id)
        except Message.DoesNotExist:
            return Response({"error": "Invalid message"}, status=400)

        # ✅ Fix #5 - handle participant not found
        try:
            participant = RoomParticipant.objects.get(user=user, room_id=room_id)
        except RoomParticipant.DoesNotExist:
            return Response({"error": "You are not part of this room"}, status=403)

        participant.last_seen_message = message
        participant.save(update_fields=["last_seen_message"])

        return Response({"message": "Seen updated"})


class SupportListAPIView(generics.ListAPIView):
    serializer_class = SupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportProfile.objects.filter(user__role="SUPPORT").select_related("user", "user__company")


class PilgrimPackagesAPIView(generics.ListAPIView):
    serializer_class = PackageWithGuideSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "pilgrim_profile"):
            return Package.objects.filter(company=user.company, status="ACTIVE")
        return Package.objects.none()


class CompanyPilgrimsAPIView(generics.ListAPIView):
    serializer_class = PilgrimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        company = None

        # ✅ Owner
        if hasattr(user, "companies") and user.companies.exists():
            company = user.companies.first()

        # ✅ Employee (NEW unified model)
        elif hasattr(user, "employee_profile"):
            company = user.employee_profile.company

        if not company:
            return User.objects.none()

        return User.objects.filter(
            bookings__package__company=company,
            bookings__status="CONFIRMED"
        ).distinct()


class CompanyEmployeesAPIView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "COMPANY" or not user.company:
            return User.objects.none()

        return User.objects.filter(company=user.company)


class PlatformEmployeesAPIView(generics.ListAPIView):
    serializer_class = PlatformStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not (hasattr(user, "staff_profile") or user.is_superuser):
            raise PermissionDenied("You must be a staff member or superuser to access this API.")

        return PlatformStaffProfile.objects.all().order_by("department", "first_name")


class DeleteGroupChat(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        user = request.user

        try:
            room = ChatRoom.objects.get(id=room_id, room_type="GROUP")
        except ChatRoom.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)

        is_admin = RoomParticipant.objects.filter(
            room=room,
            user=user,
            role="ADMIN"
        ).exists()

        if not is_admin:
            raise PermissionDenied("Only admins can delete the group")

        room.delete()

        return Response({"message": "Group deleted successfully"})


class LeaveGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user

        participant = RoomParticipant.objects.filter(
            room_id=room_id,
            user=user
        ).first()

        if not participant:
            return Response({"error": "Not in group"}, status=404)

        is_admin = participant.role == "ADMIN"

        members = RoomParticipant.objects.filter(room_id=room_id)

        # If last member → delete group
        if members.count() == 1:
            ChatRoom.objects.filter(id=room_id).delete()
            return Response({"message": "Group deleted (last member left)"})

        # If admin → assign new admin before leaving
        if is_admin:
            new_admin = members.exclude(user=user).first()
            if new_admin:
                new_admin.role = "ADMIN"
                new_admin.save()

        participant.delete()

        return Response({"message": "You left the group"})


class MakeAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        user = request.user
        user_id = request.data.get("user_id")

        # ✅ Validate user_id
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        if not RoomParticipant.objects.filter(
            room_id=room_id,
            user=user,
            role="ADMIN"
        ).exists():
            raise PermissionDenied("Only admins allowed")

        participant = RoomParticipant.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).first()

        if not participant:
            return Response({"error": "User not in group"}, status=404)

        participant.role = "ADMIN"
        participant.save()

        return Response({"message": "User promoted to admin"})


class RoomDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        user = request.user

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        if not room.participants.filter(id=user.id).exists():
            raise PermissionDenied("You are not part of this room")

        serializer = RoomDetailSerializer(room)

        return Response(serializer.data)