import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from django.db.models import Count, Q, F, OuterRef, Subquery, CharField
from django.db.models.functions import Cast, Coalesce


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"notifications_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # ✅ snapshot عند الاتصال
        snapshot = await self.get_unread_snapshot()

        await self.send(text_data=json.dumps({
            "type": "unread_snapshot",
            "data": snapshot
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": event.get("event"),
            "room_id": event.get("room_id"),
            "unread_count": event.get("unread_count"),
            "last_message": event.get("last_message"),
            "sender_id": event.get("sender_id"),
        }))

    # =========================
    # SNAPSHOT
    # =========================

    async def get_unread_snapshot(self):
        return await self._get_unread_snapshot_db()

    @sync_to_async
    def _get_unread_snapshot_db(self):
        from chat.models import ChatRoom, Message

        user = self.user

        # ✅ آخر رسالة (text أو file)
        last_message_subquery = (
            Message.objects
            .filter(room=OuterRef("pk"))
            .order_by("-id")
            .annotate(
                final_text=Coalesce(
                    "text",
                    Cast("file", output_field=CharField()),
                    output_field=CharField()  # 🔥 مهم جداً
                )
            )
            .values("final_text")[:1]
        )

        rooms = (
            ChatRoom.objects
            .filter(participants=user)
            .annotate(
                unread_count=Count(
                    "messages",
                    filter=(
                        Q(messages__id__gt=F("roomparticipant__last_seen_message")) |
                        Q(roomparticipant__last_seen_message__isnull=True)
                    ) & ~Q(messages__sender=user)
                ),
                last_message=Subquery(last_message_subquery)
            )
            .values("id", "unread_count", "last_message")
        )

        rooms_list = list(rooms)

        total_unread = sum(room["unread_count"] for room in rooms_list)

        return {
            "total_unread_all_rooms": total_unread,
            "rooms": rooms_list
        }