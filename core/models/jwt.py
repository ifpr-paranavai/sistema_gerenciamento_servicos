from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.apps import apps
import jwt
from django.conf import settings

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            # Extrair o token do cabeçalho
            auth_parts = auth_header.split()

            if auth_parts[0].lower() != 'bearer':
                return None

            if len(auth_parts) == 1:
                msg = 'Token inválido. Cabeçalho de autorização mal formado.'
                raise AuthenticationFailed(msg)
            elif len(auth_parts) > 2:
                msg = 'Token inválido. Cabeçalho de autorização com espaços não é permitido.'
                raise AuthenticationFailed(msg)

            token = auth_parts[1]

            # Decodificar o token
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido')

        try:
            # Buscar o usuário pelo UUID
            User = apps.get_model('authentication', 'User')
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuário não encontrado')

        return (user, None)