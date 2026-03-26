# from channels.layers import get_channel_layer

# async def send_room_update(user_id, room_id, unread_count, last_message, sender_id):
#     channel_layer = get_channel_layer()

#     await channel_layer.group_send(
#         f"notifications_{user_id}",
#         {
#             "type": "send_notification",
#             "event": "ROOM_UPDATE",
#             "room_id": room_id,
#             "unread_count": unread_count,
#             "last_message": last_message,
#             "sender_id": sender_id,
#         }
#     )


from django.core.cache import cache
from channels.layers import get_channel_layer

def _room_online_key(room_id: int, user_id: int) -> str:
    return f"chat_room_online_{room_id}_{user_id}"

# ✅ اجعلها async
async def send_room_update(user_id, room_id, unread_count, last_message, sender_id):
    # إذا المستخدم متصل بالغرفة اجعل unread_count = 0
    is_online_in_room = cache.get(_room_online_key(room_id, user_id), False)
    if is_online_in_room:
        unread_count = 0

    # أرسل الإشعار عبر websocket
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"notifications_{user_id}",
        {
            "type": "send_notification",
            "event": "ROOM_UPDATE",
            "room_id": room_id,
            "unread_count": unread_count,
            "last_message": last_message,
            "sender_id": sender_id,
        }
    )