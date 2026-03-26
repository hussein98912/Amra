from django.urls import path
from .views import *


urlpatterns = [
    path("create-room/", CreateChatRoom.as_view(), name="create-chat-room"),
    path("my-rooms/", UserChatRooms.as_view(), name="user-chat-rooms"),
    path("room/<int:room_id>/messages/", RoomMessages.as_view(), name="room-messages"),
    path("room/<int:room_id>/mark-seen/", MarkRoomAsSeen.as_view(), name="mark-room-seen"),
    path("create-group/", CreateGroupChat.as_view(), name="create-group-chat"),
    path("group/<int:room_id>/add-user/", AddUserToGroup.as_view(), name="add-user-group"),
    path("group/<int:room_id>/remove-user/", RemoveUserFromGroup.as_view(), name="remove-user-group"),
    path("group/<int:room_id>/delete/", DeleteGroupChat.as_view(), name="delete-group"),
    path("group/<int:room_id>/leave/", LeaveGroup.as_view()),
    path("group/<int:room_id>/make-admin/", MakeAdmin.as_view()),
    path("room/<int:room_id>/", RoomDetailAPIView.as_view()),
    path("companies/", SupportListAPIView.as_view(), name="support-list"),
    path("my-packages/", PilgrimPackagesAPIView.as_view(), name="pilgrim-packages"),
    path("company/pilgrims/", CompanyPilgrimsAPIView.as_view(), name="company-pilgrims"),
    path("company/employees/", CompanyEmployeesAPIView.as_view(), name="company-employees"),
    path("platform/employees/", PlatformEmployeesAPIView.as_view(), name="platform-employees"),
    
]   