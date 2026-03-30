# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async

# from django.db.models import Count, Q, F, OuterRef, Subquery, CharField
# from django.db.models.functions import Cast, Coalesce


# class NotificationConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.user = self.scope["user"]

#         if self.user.is_anonymous:
#             await self.close()
#             return

#         self.group_name = f"notifications_{self.user.id}"

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         await self.accept()

#         # ✅ snapshot عند الاتصال
#         snapshot = await self.get_unread_snapshot()

#         await self.send(text_data=json.dumps({
#             "type": "unread_snapshot",
#             "data": snapshot
#         }))

#     async def disconnect(self, close_code):
#         if hasattr(self, "group_name"):
#             await self.channel_layer.group_discard(
#                 self.group_name,
#                 self.channel_name
#             )

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({
#             "type": event.get("event"),
#             "room_id": event.get("room_id"),
#             "unread_count": event.get("unread_count"),
#             "last_message": event.get("last_message"),
#             "sender_id": event.get("sender_id"),
#         }))

#     # =========================
#     # SNAPSHOT
#     # =========================

#     async def get_unread_snapshot(self):
#         return await self._get_unread_snapshot_db()

#     @sync_to_async
#     def _get_unread_snapshot_db(self):
#         from chat.models import ChatRoom, Message

#         user = self.user

#         # ✅ آخر رسالة (text أو file)
#         last_message_subquery = (
#             Message.objects
#             .filter(room=OuterRef("pk"))
#             .order_by("-id")
#             .annotate(
#                 final_text=Coalesce(
#                     "text",
#                     Cast("file", output_field=CharField()),
#                     output_field=CharField()  # 🔥 مهم جداً
#                 )
#             )
#             .values("final_text")[:1]
#         )

#         rooms = (
#             ChatRoom.objects
#             .filter(participants=user)
#             .annotate(
#                 unread_count=Count(
#                     "messages",
#                     filter=(
#                         Q(messages__id__gt=F("roomparticipant__last_seen_message")) |
#                         Q(roomparticipant__last_seen_message__isnull=True)
#                     ) & ~Q(messages__sender=user)
#                 ),
#                 last_message=Subquery(last_message_subquery)
#             )
#             .values("id", "unread_count", "last_message")
#         )

#         rooms_list = list(rooms)

#         total_unread = sum(room["unread_count"] for room in rooms_list)

#         return {
#             "total_unread_all_rooms": total_unread,
#             "rooms": rooms_list
#         }
    




# import json
# import logging
 
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from django.db.models import Count, Q, F, OuterRef, Subquery, CharField
# from django.db.models.functions import Cast, Coalesce
 
# from .presence import (
#     user_connected,
#     user_disconnected,
#     get_last_seen,
#     is_user_online,
# )
 
# logger = logging.getLogger(__name__)
 
 
# class NotificationConsumer(AsyncWebsocketConsumer):
 
#     async def connect(self):
#         self.user = self.scope["user"]
 
#         if self.user.is_anonymous:
#             await self.close(code=4001)
#             return
 
#         self.group_name = f"notifications_{self.user.id}"
 
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
 
#         await self.accept()
 
#         # ✅ Increment counter — only broadcast if first connection
#         was_offline = await self._connect_presence()
#         if was_offline:
#             await self._broadcast_presence(True)
#             logger.info(f"User {self.user.id} is now online")
 
#         # ✅ Send unread snapshot on connect
#         snapshot = await self.get_unread_snapshot()
#         await self.send(text_data=json.dumps({
#             "type": "unread_snapshot",
#             "data": snapshot
#         }))
 
#     async def disconnect(self, close_code):
#         if not hasattr(self, "group_name"):
#             return
 
#         # ✅ Decrement counter — only broadcast if last connection
#         went_offline = await self._disconnect_presence()
#         if went_offline:
#             await self._broadcast_presence(False)
#             logger.info(f"User {self.user.id} is now offline")
 
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )
 
#     async def receive(self, text_data):
#         """Handle messages sent from the client."""
#         try:
#             data = json.loads(text_data)
#         except json.JSONDecodeError:
#             return
 
#         # ✅ Keepalive ping — important for mobile connections
#         if data.get("type") == "ping":
#             await self.send(text_data=json.dumps({"type": "pong"}))
 
#     # =========================
#     # Handlers (called by group_send)
#     # =========================
 
#     async def send_notification(self, event):
#         """Handles room update notifications pushed from chat."""
#         await self.send(text_data=json.dumps({
#             "type": event.get("event"),
#             "room_id": event.get("room_id"),
#             "unread_count": event.get("unread_count"),
#             "last_message": event.get("last_message"),
#             "sender_id": event.get("sender_id"),
#         }))
 
#     async def presence_update(self, event):
#         """
#         Called when a contact comes online or goes offline.
#         Pushes presence event to the frontend instantly.
#         """
#         await self.send(text_data=json.dumps({
#             "type": "presence",
#             "user_id": event["user_id"],
#             "is_online": event["is_online"],
#             "last_seen": event.get("last_seen"),  # shown when offline
#         }))
 
#     # =========================
#     # Presence Helpers
#     # =========================
 
#     @sync_to_async
#     def _connect_presence(self) -> bool:
#         """
#         Increment connection counter.
#         Returns True if user was offline (first tab opened).
#         """
#         return user_connected(self.user.id)
 
#     @sync_to_async
#     def _disconnect_presence(self) -> bool:
#         """
#         Decrement connection counter.
#         Returns True if user is now offline (last tab closed).
#         """
#         return user_disconnected(self.user.id)
 
#     @sync_to_async
#     def _get_contacts(self):
#         """
#         Get IDs of all users who share at least one room with this user.
#         These are the people who need to be notified about presence changes.
#         """
#         from chat.models import ChatRoom
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
 
#         room_ids = ChatRoom.objects.filter(
#             participants=self.user
#         ).values_list("id", flat=True)
 
#         return list(
#             User.objects
#             .filter(chat_rooms__id__in=room_ids)
#             .exclude(id=self.user.id)
#             .values_list("id", flat=True)
#             .distinct()
#         )
 
#     async def _broadcast_presence(self, is_online: bool):
#         """
#         Notify every contact of this user about their online/offline status.
#         Only called when status actually changes (first/last connection).
#         """
#         contact_ids = await self._get_contacts()
 
#         # Get last seen only when going offline
#         last_seen = None
#         if not is_online:
#             last_seen = get_last_seen(self.user.id)
 
#         for contact_id in contact_ids:
#             await self.channel_layer.group_send(
#                 f"notifications_{contact_id}",
#                 {
#                     "type": "presence_update",
#                     "user_id": self.user.id,
#                     "is_online": is_online,
#                     "last_seen": last_seen,
#                 }
#             )
 
#     # =========================
#     # Snapshot
#     # =========================
 
#     async def get_unread_snapshot(self):
#         return await self._get_unread_snapshot_db()
 
#     @sync_to_async
#     def _get_unread_snapshot_db(self):
#         from chat.models import ChatRoom, Message
 
#         user = self.user
 
#         last_message_subquery = (
#             Message.objects
#             .filter(room=OuterRef("pk"))
#             .order_by("-id")
#             .annotate(
#                 final_text=Coalesce(
#                     "text",
#                     Cast("file", output_field=CharField()),
#                     output_field=CharField()
#                 )
#             )
#             .values("final_text")[:1]
#         )
 
#         rooms = (
#             ChatRoom.objects
#             .filter(participants=user)
#             .filter(roomparticipant__user=user)
#             .annotate(
#                 unread_count=Count(
#                     "messages",
#                     filter=(
#                         (
#                             Q(messages__id__gt=F("roomparticipant__last_seen_message")) |
#                             Q(roomparticipant__last_seen_message__isnull=True)
#                         )
#                         & ~Q(messages__sender=user)
#                     )
#                 ),
#                 last_message=Subquery(last_message_subquery)
#             )
#             .values("id", "unread_count", "last_message")
#         )
 
#         rooms_list    = list(rooms)
#         total_unread  = sum(room["unread_count"] for room in rooms_list)
 
#         return {
#             "total_unread_all_rooms": total_unread,
#             "rooms": rooms_list
#         }


import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.db.models import Count, Q, F, OuterRef, Subquery, CharField
from django.db.models.functions import Cast, Coalesce

from .presence import (
    user_connected,
    user_disconnected,
    get_last_seen,
    is_user_online,
)

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.group_name = f"notifications_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # ✅ Increment counter — only broadcast if first connection
        was_offline = await self._connect_presence()
        if was_offline:
            await self._broadcast_presence(True)
            logger.info(f"User {self.user.id} is now online")

        # ✅ Send unread snapshot on connect
        unread_snapshot = await self.get_unread_snapshot()
        await self.send(text_data=json.dumps({
            "type": "unread_snapshot",
            "data": unread_snapshot
        }))

        # 🔹 Send presence snapshot for all contacts
        contacts = await self._get_contacts()  # list of contact IDs

        presence_data = []
        for uid in contacts:
            online = await sync_to_async(is_user_online)(uid)
            last_seen = None if online else await sync_to_async(get_last_seen)(uid)
            presence_data.append({
                "user_id": uid,
                "is_online": online,
                "last_seen": last_seen
            })

        await self.send(text_data=json.dumps({
            "type": "presence_snapshot",
            "data": presence_data
        }))

    async def disconnect(self, close_code):
        if not hasattr(self, "group_name"):
            return

        # ✅ Decrement counter — only broadcast if last connection
        went_offline = await self._disconnect_presence()
        if went_offline:
            await self._broadcast_presence(False)
            logger.info(f"User {self.user.id} is now offline")

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages sent from the client."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # ✅ Keepalive ping — important for mobile connections
        if data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    # =========================
    # Handlers (called by group_send)
    # =========================

    async def send_notification(self, event):
        """
        Handles room update notifications pushed from chat.
        Computes per-room and total unread deltas.
        """
        if event.get("event") == "ticket_status_update":
            await self.send(text_data=json.dumps({
                "type": "ticket_status_update",
                "ticket_id": event.get("ticket_id"),
                "status": event.get("status"),
                "updated_by": event.get("updated_by"),
                "message": event.get("message")
            }))
            return  # skip chat logic
        
        room_id = event.get("room_id")
        unread_count = event.get("unread_count")  # new unread for this room

        # Fetch previous snapshot from DB or cache
        snapshot = await self.get_unread_snapshot()
        prev_room_unread = 0
        prev_total_unread = snapshot["total_unread_all_rooms"]

        for room in snapshot["rooms"]:
            if room["id"] == room_id:
                prev_room_unread = room["unread_count"]
                break

        # Compute deltas
        new_room_count = unread_count
        new_total_unread = prev_total_unread - prev_room_unread + unread_count

        await self.send(text_data=json.dumps({
            "type": event.get("event"),
            "room_id": room_id,
            "last_message": event.get("last_message"),
            "sender_id": event.get("sender_id"),
            "new_room_count": new_room_count,
            "new_total_unread": new_total_unread,
        }))

    async def presence_update(self, event):
        """
        Called when a contact comes online or goes offline.
        Pushes presence event to the frontend instantly.
        """
        await self.send(text_data=json.dumps({
            "type": "presence",
            "user_id": event["user_id"],
            "is_online": event["is_online"],
            "last_seen": event.get("last_seen"),  # shown when offline
        }))

    # =========================
    # Presence Helpers
    # =========================

    @sync_to_async
    def _connect_presence(self) -> bool:
        """
        Increment connection counter.
        Returns True if user was offline (first tab opened).
        """
        return user_connected(self.user.id)

    @sync_to_async
    def _disconnect_presence(self) -> bool:
        """
        Decrement connection counter.
        Returns True if user is now offline (last tab closed).
        """
        return user_disconnected(self.user.id)

    @sync_to_async
    def _get_contacts(self):
        """
        Get IDs of all users who share at least one room with this user.
        These are the people who need to be notified about presence changes.
        """
        from chat.models import ChatRoom
        from django.contrib.auth import get_user_model
        User = get_user_model()

        room_ids = ChatRoom.objects.filter(
            participants=self.user
        ).values_list("id", flat=True)

        return list(
            User.objects
            .filter(chat_rooms__id__in=room_ids)
            .exclude(id=self.user.id)
            .values_list("id", flat=True)
            .distinct()
        )

    async def _broadcast_presence(self, is_online: bool):
        """
        Notify every contact of this user about their online/offline status.
        Only called when status actually changes (first/last connection).
        """
        contact_ids = await self._get_contacts()

        # Get last seen only when going offline
        last_seen = None
        if not is_online:
            last_seen = get_last_seen(self.user.id)

        for contact_id in contact_ids:
            await self.channel_layer.group_send(
                f"notifications_{contact_id}",
                {
                    "type": "presence_update",
                    "user_id": self.user.id,
                    "is_online": is_online,
                    "last_seen": last_seen,
                }
            )

    # =========================
    # Snapshot (Unread Messages)
    # =========================

    async def get_unread_snapshot(self):
        return await self._get_unread_snapshot_db()

    @sync_to_async
    def _get_unread_snapshot_db(self):
        from chat.models import ChatRoom, Message

        user = self.user

        last_message_subquery = (
            Message.objects
            .filter(room=OuterRef("pk"))
            .order_by("-id")
            .annotate(
                final_text=Coalesce(
                    "text",
                    Cast("file", output_field=CharField()),
                    output_field=CharField()
                )
            )
            .values("final_text")[:1]
        )

        rooms = (
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
 