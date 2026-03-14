import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Message, ChatRoom
from notifications.models import Notification


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message = data.get("message")
        sender = data.get("sender")
        typing = data.get("typing")

        if typing:

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_event",
                    "user": sender
                }
            )

            return

        msg = await self.save_message(sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg.text,
                "sender": sender
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"]
        }))

    async def typing_event(self, event):

        await self.send(text_data=json.dumps({
            "type": "typing",
            "user": event["user"]
        }))

    @sync_to_async
    def save_message(self, sender, message):

        room = ChatRoom.objects.get(id=self.room_id)

        msg = Message.objects.create(
            room=room,
            sender_id=sender,
            text=message
        )

        for user in room.participants.all():

            if user.id != sender:

                Notification.objects.create(
                    user=user,
                    message="New chat message"
                )

        return msg