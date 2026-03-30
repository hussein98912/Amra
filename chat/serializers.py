from rest_framework import serializers
from .models import ChatRoom, Message, RoomParticipant
from companies.models import SupportProfile
from packages.models import Package
from users.models import User
from platform_admin.models import PlatformStaffProfile

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source="sender.email", read_only=True)
    seen = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"  # Or list explicitly, including 'seen'

    def get_seen(self, obj):
        user = self.context.get("request").user
        return user in obj.seen_by.all()


class ChatRoomSerializer(serializers.ModelSerializer):

    participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def get_participants(self, obj):

        users = obj.participants.all()

        return [
            {
                "id": u.id,
                "email": u.email
            }
            for u in users
        ]
    

class SupportSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email")
    company_name = serializers.CharField(source="user.company.name")
    user_id = serializers.IntegerField(source="user.id", read_only=True) 

    class Meta:
        model = SupportProfile
        fields = ["id", "user_id", "full_name", "email", "company_name", "notes"]

    def get_full_name(self, obj):
        return f"{obj.user.email}"




class PackageWithGuideSerializer(serializers.ModelSerializer):
    guide_name = serializers.SerializerMethodField()
    support_staff = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "package_type",
            "price",
            "guide_name",
            "support_staff",
        ]

    def get_guide_name(self, obj):
        if obj.guide:
            return obj.guide.email  # أو obj.guide.get_full_name() لو موجود
        return None

    def get_support_staff(self, obj):
        supports = SupportProfile.objects.filter(user__company=obj.company)
        return SupportSerializer(supports, many=True).data  
    


class PilgrimSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "phone"]

    def get_full_name(self, obj):
        profile = getattr(obj, "pilgrim_profile", None)
        return profile.full_name if profile else obj.email

    def get_phone(self, obj):
        profile = getattr(obj, "pilgrim_profile", None)
        return profile.phone if profile else None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context["request"].user

        if user.role not in ["COMPANY", "GUIDE"]:
            data.pop("email", None)
            data.pop("phone", None)

        return data
    

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "role", "status", "full_name"]

    def get_full_name(self, obj):
        # If the user is a pilgrim, get pilgrim_profile full_name
        if hasattr(obj, "pilgrim_profile"):
            return obj.pilgrim_profile.full_name
        # Otherwise, fallback to email
        return obj.email
    


class PlatformStaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")  # Get email from related User
    role = serializers.CharField(source="user.role")     # Optional, if you want role

    class Meta:
        model = PlatformStaffProfile
        fields = [
            "id",
            "user_id",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "department",
            "job_title",
            "profile_image",
            "created_at"
        ]

class RoomParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id")
    email = serializers.CharField(source="user.email")

    class Meta:
        model = RoomParticipant
        fields = ["user_id", "email", "role", "joined_at"]


class RoomDetailSerializer(serializers.ModelSerializer):
    participants = RoomParticipantSerializer(
        source="roomparticipant_set", many=True
    )

    class Meta:
        model = ChatRoom
        fields = ["id", "name", "room_type", "participants", "created_at"]



class ChatRoomWithMetaSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    unread_messages = serializers.IntegerField(source="unread_count", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "room_type",
            "participants",
            "unread_messages",
            "last_message",
            "created_at",
        ]

    def get_participants(self, obj):
        data = []

        for u in obj.participants.all():
            name = None

            # ✅ 1. PILGRIM
            if u.role == "PILGRIM" and hasattr(u, "pilgrim_profile"):
                name = u.pilgrim_profile.full_name

            # ✅ 2. COMPANY OWNER
            elif u.role == "COMPANY" and u.company:
                name = u.company.name

            # ✅ 3. COMPANY EMPLOYEES (GUIDE / FINANCE)
            elif u.role in ["GUIDE", "FINANCE"]:
                # If they belong to a company
                if u.company:
                    # Try to get personal name later if you add profile
                    name = u.company.name

            # ✅ 4. PLATFORM STAFF (SUPPORT / FINANCE in platform)
            if hasattr(u, "staff_profile"):
                staff = u.staff_profile
                name = f"{staff.first_name} {staff.last_name}".strip()

            # ✅ 5. FALLBACK (very important)   
            if not name:
                name = u.email

            data.append({
                "id": u.id,
                "email": u.email,
                "name": name
            })

        return data

    def get_last_message(self, obj):
        if not obj.last_message_text:
            return None

        return {
            "content": obj.last_message_text,
            "sender": obj.last_message_sender,
            "created_at": obj.last_message_time
        }