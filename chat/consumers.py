import json
import logging
from typing import Any

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import ChatRoom, Message
from notifications.utils import send_room_update

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self) -> None:
        self.user = self.scope.get("user")

        if not await self._is_authenticated():
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"User {self.user.id} joined {self.room_group_name}")

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("Invalid JSON format")
            return

        message = data.get("message")
        if not message:
            await self._send_error("Message field is required")
            return

        # ✅ 1. Save message
        msg = await self._create_message(message)

        # ✅ 2. Get participants except sender
        participants = await self._get_other_participants()

        # ✅ 3. Send aggregated updates
        for user in participants:

            unread_count = await self._get_unread_count(user.id)

            await send_room_update(
                user_id=user.id,
                room_id=self.room_id,
                unread_count=unread_count,
                last_message=self._get_preview(msg.text),
                sender_id=self.user.id
            )

        # ✅ 4. Broadcast message
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
    def _create_message(self, text):
        return Message.objects.create(
            room_id=self.room_id,
            sender=self.user,
            text=text
        )

    @database_sync_to_async
    def _get_other_participants(self):
        room = ChatRoom.objects.get(id=self.room_id)
        return list(room.participants.exclude(id=self.user.id))

    @database_sync_to_async
    def _get_unread_count(self, user_id):
        return Message.objects.filter(
            room_id=self.room_id
        ).exclude(seen_by__id=user_id).count()

    # ----------------------
    # Helpers
    # ----------------------

    def _get_preview(self, text):
        if not text:
            return "File"
        return text[:30]

    async def _is_authenticated(self) -> bool:
        if self.user.is_anonymous:
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