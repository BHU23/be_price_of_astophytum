from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
class ExpiringTokenAuthentication(TokenAuthentication):
    expiration_duration = timedelta(hours=6)
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        expiration_time = token.created + self.expiration_duration
        if timezone.now() > expiration_time:
            token.delete()
            raise AuthenticationFailed('Token has expired')

        return token.user, token