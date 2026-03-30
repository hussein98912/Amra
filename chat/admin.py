from django.contrib import admin
from .models import ChatRoom, RoomParticipant, Message


class RoomParticipantInline(admin.TabularInline):
    model = RoomParticipant
    extra = 0
    autocomplete_fields = ["user"]
    readonly_fields = ["joined_at", "last_seen_message"]


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["sender", "created_at"]
    fields = ["sender", "text", "file", "created_at"]
    autocomplete_fields = ["sender"]


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "room_type", "created_by", "created_at"]
    list_filter = ["room_type", "created_at"]
    search_fields = ["name", "created_by__email"]
    autocomplete_fields = ["created_by", "participants"]
    inlines = [RoomParticipantInline, MessageInline]
    ordering = ["-created_at"]


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "room", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    search_fields = ["user__email", "room__name"]
    autocomplete_fields = ["user", "room"]
    ordering = ["-joined_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "sender", "created_at"]
    list_filter = ["created_at", "room"]
    search_fields = ["text", "sender__email", "room__name"]
    autocomplete_fields = ["sender", "room"]
    ordering = ["-created_at"]