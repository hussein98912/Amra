from django.db import models
from users.models import User


class ChatRoom(models.Model):

    ROOM_TYPES = (
        ("PRIVATE", "Private Chat"),
        ("GROUP", "Group Chat"),
    )

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES,
        default="PRIVATE"
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    participants = models.ManyToManyField(
        User,
        through="RoomParticipant",
        related_name="chat_rooms"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_rooms"
    )

    created_at = models.DateTimeField(auto_now_add=True)


class RoomParticipant(models.Model):

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("MEMBER", "Member"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="MEMBER"
    )

    joined_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.TextField(blank=True)

    file = models.FileField(
        upload_to="chat/files/",
        null=True,
        blank=True
    )

    seen_by = models.ManyToManyField(
        User,
        related_name="seen_messages",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)