from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, ContactPresenceAPIView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename="notifications")

urlpatterns = [
    # ✅ ViewSet routes
    *router.urls,

    # ✅ Presence API
    path("presence/", ContactPresenceAPIView.as_view(), name="contact-presence"),
]