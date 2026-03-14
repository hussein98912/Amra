import os
# ✅ Make sure this is set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Amra.settings")
import django
django.setup()  # ensure apps are loaded before importing models

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chat.routing



application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})