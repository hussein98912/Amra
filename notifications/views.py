from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from .presence import is_user_online, get_last_seen


class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactPresenceAPIView(APIView):
    """
    Returns online/offline + last seen for all contacts
    of the logged-in user. Call this once on app load
    to get initial presence state before WebSocket events arrive.
    """
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        from chat.models import ChatRoom
        from django.contrib.auth import get_user_model
        User = get_user_model()
 
        user = request.user
 
        room_ids = ChatRoom.objects.filter(
            participants=user
        ).values_list("id", flat=True)
 
        contact_ids = (
            User.objects
            .filter(chat_rooms__id__in=room_ids)
            .exclude(id=user.id)
            .distinct()
            .values_list("id", flat=True)
        )
 
        result = []
        for uid in contact_ids:
            online = is_user_online(uid)
            result.append({
                "user_id": uid,
                "is_online": online,
                "last_seen": None if online else get_last_seen(uid),
            })
 
        return Response(result)