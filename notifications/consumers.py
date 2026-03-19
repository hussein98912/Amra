import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONNECTED USER:", self.scope["user"])
        print("USER ID:", self.scope["user"].id if self.scope["user"] else None)

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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": event.get("event"),  # ROOM_UPDATE
            "room_id": event.get("room_id"),
            "unread_count": event.get("unread_count"),
            "last_message": event.get("last_message"),
            "sender_id": event.get("sender_id"),
        }))