import json
import logging
from typing import Any
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat rooms.
    Handles connection, disconnection, receiving, and broadcasting messages.
    """

    async def connect(self) -> None:
        """Handle WebSocket connection."""
        self.user = self.scope.get("user")
        if not await self._is_authenticated():
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self._send_debug_message("Connected to room!")
        logger.info(f"User {self.user.id} joined {self.room_group_name} on channel {self.channel_name}")

    async def disconnect(self, close_code: int) -> None:
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"User {self.user.id} left {self.room_group_name} (code: {close_code})")

    async def receive(self, text_data: str) -> None:
        """Receive message from WebSocket and broadcast to room."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("Invalid JSON format")
            return

        message = data.get("message")
        if not message:
            await self._send_error("Message field is required")
            return

        logger.debug(f"Received message from {self.user.id}: {message}")

        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.id,
            }
        )

    async def chat_message(self, event: dict[str, Any]) -> None:
        """Receive message from room group and send to WebSocket."""
        await self.send_json({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
        })

    # ----------------------
    # Helper Methods
    # ----------------------

    async def _is_authenticated(self) -> bool:
        """Check if the user is authenticated, close connection if anonymous."""
        if self.user.is_anonymous:
            await self.close(code=4001)  # 4001 = unauthorized
            return False
        return True

    async def _send_debug_message(self, message: str) -> None:
        """Send a debug message to the WebSocket."""
        await self.send_json({"type": "debug", "message": message})

    async def _send_error(self, error: str) -> None:
        """Send an error message to the WebSocket."""
        await self.send_json({"type": "error", "message": error})

    async def send_json(self, content: dict[str, Any]) -> None:
        """Helper to send JSON data through WebSocket."""
        await self.send(text_data=json.dumps(content))