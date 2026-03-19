import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Amra.settings")

import django
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware

# ✅ دمج المسارات
websocket_urlpatterns = chat_websocket_urlpatterns + notifications_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})