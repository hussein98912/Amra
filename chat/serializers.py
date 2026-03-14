from rest_framework import serializers
from .models import ChatRoom, Message, RoomParticipant


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source="sender.email", read_only=True)
    seen = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"  # Or list explicitly, including 'seen'

    def get_seen(self, obj):
        user = self.context.get("request").user
        return user in obj.seen_by.all()


class ChatRoomSerializer(serializers.ModelSerializer):

    participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def get_participants(self, obj):

        users = obj.participants.all()

        return [
            {
                "id": u.id,
                "email": u.email
            }
            for u in users
        ]