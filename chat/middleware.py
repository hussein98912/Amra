# chat/middleware.py

import jwt
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.conf import settings
from users.models import User
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()  # ✅ FIX


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        token_list = params.get("token")
        user = AnonymousUser()  # ✅ default

        if token_list:
            token = token_list[0]
            user = await get_user_from_jwt(token)

        scope["user"] = user

        return await super().__call__(scope, receive, send)