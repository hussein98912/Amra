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

    class Meta:
        model = SupportProfile
        fields = ["id", "full_name", "email", "company_name", "notes"]

    def get_full_name(self, obj):
        return f"{obj.user.email}"  # إذا عندك حقل الاسم عند SupportUser غير email استخدمه




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
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name"]

    def get_full_name(self, obj):
        if hasattr(obj, "pilgrim_profile"):
            return obj.pilgrim_profile.full_name
        return obj.email
    

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