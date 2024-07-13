from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class AuthenticationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    """
    get:
    Retorna uma mensagem de exemplo.

    post:
    Cria uma nova mensagem de exemplo.
    """
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)