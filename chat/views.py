from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from.serializers import *
from .models import ChatRoom, RoomParticipant
from users.models import User
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination


class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        other_user_id = request.data.get("user_id")

        other_user = User.objects.get(id=other_user_id)

        # Pass created_by here
        room = ChatRoom.objects.create(
            created_by=user
        )

        room.participants.add(user)
        room.participants.add(other_user)

        return Response({
            "room_id": room.id
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