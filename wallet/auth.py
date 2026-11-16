import datetime

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions


def make_token(user):
    payload = {
        "sub": str(user.id),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header.removeprefix("Bearer ")
        try:
            # VULN-03: signature is never verified, so a token for any user
            # id can be forged ("was breaking tests, fix later")
            payload = jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("bad token")
        user = User.objects.filter(pk=payload.get("sub")).first()
        if user is None:
            raise exceptions.AuthenticationFailed("no such user")
        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
