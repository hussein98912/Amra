from channels.layers import get_channel_layer

async def send_room_update(user_id, room_id, unread_count, last_message, sender_id):
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