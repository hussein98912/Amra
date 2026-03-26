# import json
# import logging
# from typing import Any

# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async

# from .models import ChatRoom, Message
# from notifications.utils import send_room_update

# logger = logging.getLogger(__name__)


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self) -> None:
#         self.user = self.scope.get("user")

#         if not await self._is_authenticated():
#             return

#         self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
#         self.room_group_name = f"chat_{self.room_id}"

#         # ✅ Fix #2 - check room membership before allowing connection
#         if not await self._is_room_participant():
#             await self.accept()       # must accept before closing with custom code
#             await self.close(code=4003)
#             return

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#         logger.info(f"User {self.user.id} joined {self.room_group_name}")

#     async def disconnect(self, close_code: int) -> None:
#         if hasattr(self, "room_group_name"):
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )

#     async def receive(self, text_data: str) -> None:
#         try:
#             data = json.loads(text_data)
#         except json.JSONDecodeError:
#             await self._send_error("Invalid JSON format")
#             return

#         message = data.get("message")
#         if not message or not message.strip():
#             await self._send_error("Message field is required")
#             return

#         # ✅ 1. Save message
#         msg = await self._create_message(message.strip())

#         # ✅ 2. Get participants except sender
#         participants = await self._get_other_participants()

#         # ✅ 3. Send aggregated updates
#         for user in participants:
#             unread_count = await self._get_unread_count(user.id)

#             await send_room_update(
#                 user_id=user.id,
#                 room_id=self.room_id,
#                 unread_count=unread_count,
#                 last_message=self._get_preview(msg.text),
#                 sender_id=self.user.id
#             )

#         # ✅ 4. Broadcast message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message": msg.text,
#                 "sender": self.user.id,
#                 "room_id": self.room_id,
#                 "message_id": msg.id,
#             }
#         )

#     async def chat_message(self, event: dict[str, Any]) -> None:
#         await self.send_json({
#             "type": "message",
#             "message": event["message"],
#             "sender": event["sender"],
#             "room_id": event["room_id"],
#             "message_id": event["message_id"],
#         })

#     # ----------------------
#     # DB Helpers
#     # ----------------------

#     @database_sync_to_async
#     def _is_room_participant(self) -> bool:
#         # ✅ Fix #2 - verify user is a participant of this room
#         return ChatRoom.objects.filter(
#             id=self.room_id,
#             participants=self.user
#         ).exists()

#     @database_sync_to_async
#     def _create_message(self, text: str) -> Message:
#         return Message.objects.create(
#             room_id=self.room_id,
#             sender=self.user,
#             text=text
#         )

#     @database_sync_to_async
#     def _get_other_participants(self) -> list:
#         # ✅ Fix #9 - only fetch id field, handle missing room gracefully
#         try:
#             return list(
#                 ChatRoom.objects
#                 .get(id=self.room_id)
#                 .participants
#                 .exclude(id=self.user.id)
#                 .only("id")
#             )
#         except ChatRoom.DoesNotExist:
#             return []

#     @database_sync_to_async
#     def _get_unread_count(self, user_id: int) -> int:
#         from .models import RoomParticipant
#         try:
#             participant = RoomParticipant.objects.get(
#                 room_id=self.room_id,
#                 user_id=user_id
#             )
#             last_seen_id = participant.last_seen_message_id

#             qs = Message.objects.filter(
#                 room_id=self.room_id
#             ).exclude(sender_id=user_id)

#             if last_seen_id:
#                 qs = qs.filter(id__gt=last_seen_id)

#             return qs.count()

#         except RoomParticipant.DoesNotExist:
#             return 0

#     # ----------------------
#     # Helpers
#     # ----------------------

#     def _get_preview(self, text: str) -> str:
#         if not text:
#             return "File"
#         return text[:30]

#     async def _is_authenticated(self) -> bool:
#         if not self.user or self.user.is_anonymous:
#             await self.close(code=4001)
#             return False
#         return True

#     async def _send_error(self, error: str) -> None:
#         await self.send_json({
#             "type": "error",
#             "message": error
#         })

#     async def send_json(self, content: dict[str, Any]) -> None:
#         await self.send(text_data=json.dumps(content))



import json
import logging
from typing import Any

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache

from .models import ChatRoom, Message, RoomParticipant
from notifications.utils import send_room_update

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat with automatic presence + unread tracking"""

    async def connect(self) -> None:
        self.user = self.scope.get("user")

        if not await self._is_authenticated():
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # التحقق من أن المستخدم مشارك بالغرفة
        if not await self._is_room_participant():
            await self.accept()  # must accept before closing
            await self.close(code=4003)
            return

        # إضافة المستخدم لمجموعة الغرفة
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"User {self.user.id} joined {self.room_group_name}")

        # ✅ علامة أن المستخدم متصل بالغرفة
        await self._set_user_online_in_room()

        # ✅ تحديث آخر رسالة مقروءة (mark all as seen عند الدخول)
        await self._mark_messages_as_seen()

    async def disconnect(self, close_code: int) -> None:
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        await self._set_user_offline_in_room()

    async def receive(self, text_data: str) -> None:
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("Invalid JSON format")
            return

        message = data.get("message")
        if not message or not message.strip():
            await self._send_error("Message field is required")
            return

        # 1️⃣ حفظ الرسالة
        msg = await self._create_message(message.strip())

        # 2️⃣ الحصول على المشاركين الآخرين
        participants = await self._get_other_participants()

        # 3️⃣ تحديث الرسائل كـ seen لكل مشارك متصل بالغرفة
        for user in participants:
            unread_count = await self._get_unread_count(user.id)

            await send_room_update(
                user_id=user.id,
                room_id=self.room_id,
                unread_count=unread_count,
                last_message=self._get_preview(msg.text),
                sender_id=self.user.id
            )

        # 4️⃣ بث الرسالة لجميع المستخدمين في الغرفة
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg.text,
                "sender": self.user.id,
                "room_id": self.room_id,
                "message_id": msg.id,
            }
        )

    async def chat_message(self, event: dict[str, Any]) -> None:
        await self.send_json({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
            "room_id": event["room_id"],
            "message_id": event["message_id"],
        })

    # ----------------------
    # DB Helpers
    # ----------------------
    @database_sync_to_async
    def _is_room_participant(self) -> bool:
        return ChatRoom.objects.filter(
            id=self.room_id,
            participants=self.user
        ).exists()

    @database_sync_to_async
    def _create_message(self, text: str) -> Message:
        return Message.objects.create(
            room_id=self.room_id,
            sender=self.user,
            text=text
        )

    @database_sync_to_async
    def _get_other_participants(self) -> list:
        try:
            return list(
                ChatRoom.objects
                .get(id=self.room_id)
                .participants
                .exclude(id=self.user.id)
                .only("id")
            )
        except ChatRoom.DoesNotExist:
            return []

    @database_sync_to_async
    def _get_unread_count(self, user_id: int) -> int:
        # 1️⃣ تحقق إذا المستخدم متصل بالغرفة
        is_online_in_room = cache.get(f"chat_room_online_{self.room_id}_{user_id}", False)
        if is_online_in_room:
            return 0

        try:
            participant = RoomParticipant.objects.get(
                room_id=self.room_id,
                user_id=user_id
            )
            last_seen_id = participant.last_seen_message_id

            qs = Message.objects.filter(room_id=self.room_id).exclude(sender_id=user_id)
            if last_seen_id:
                qs = qs.filter(id__gt=last_seen_id)

            return qs.count()
        except RoomParticipant.DoesNotExist:
            return 0

    @database_sync_to_async
    def _mark_messages_as_seen(self):
        """عند دخول المستخدم للغرفة، جميع الرسائل التي لم يراها تصبح مقروءة"""
        participant, _ = RoomParticipant.objects.get_or_create(
            room_id=self.room_id,
            user=self.user
        )
        last_message = Message.objects.filter(room_id=self.room_id).order_by("-id").first()
        if last_message:
            participant.last_seen_message = last_message
            participant.save()

    # ----------------------
    # Room online tracking
    # ----------------------
    @database_sync_to_async
    def _set_user_online_in_room(self):
        key = f"chat_room_online_{self.room_id}_{self.user.id}"
        cache.set(key, True, timeout=24*3600)

    @database_sync_to_async
    def _set_user_offline_in_room(self):
        key = f"chat_room_online_{self.room_id}_{self.user.id}"
        cache.delete(key)

    @database_sync_to_async
    def _is_user_online_in_room(self, user_id: int) -> bool:
        key = f"chat_room_online_{self.room_id}_{user_id}"
        return cache.get(key, False)

    # ----------------------
    # Helpers
    # ----------------------
    def _get_preview(self, text: str) -> str:
        if not text:
            return "File"
        return text[:30]

    async def _is_authenticated(self) -> bool:
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return False
        return True

    async def _send_error(self, error: str) -> None:
        await self.send_json({
            "type": "error",
            "message": error
        })

    async def send_json(self, content: dict[str, Any]) -> None:
        await self.send(text_data=json.dumps(content))