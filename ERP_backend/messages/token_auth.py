"""
WebSocket JWT 인증 미들웨어
- erp-access 쿠키 또는 ?token= 쿼리 파라미터에서 JWT 추출
"""
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_key):
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import TokenError
    try:
        token = AccessToken(token_key)
        user_id = token['user_id']
        return User.objects.select_related('employee').get(id=user_id)
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = None

        # 1) Cookie 에서 erp-access 추출
        headers = dict(scope.get('headers', []))
        if b'cookie' in headers:
            cookie_str = headers[b'cookie'].decode('utf-8', errors='replace')
            for item in cookie_str.split(';'):
                item = item.strip()
                if item.startswith('erp-access='):
                    token = item[len('erp-access='):]
                    break

        # 2) 없으면 query string ?token=... 시도
        if not token:
            qs = parse_qs(scope.get('query_string', b'').decode('utf-8'))
            token_list = qs.get('token', [])
            if token_list:
                token = token_list[0]

        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)
