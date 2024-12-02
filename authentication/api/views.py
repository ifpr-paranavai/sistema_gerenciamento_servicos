from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from authentication.api.serializers import ProviderScheduleSerializer, SimpleUserSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from authentication.models import User
from core.models.mixins import DynamicViewPermissions
from core.models.role import Role

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

class UserViewSet(ViewSet):
    permission_classes = [DynamicViewPermissions]
    serializer_class = SimpleUserSerializer

    @action(detail=False, methods=['get'])
    def clients(self, request):
        users = User.objects.filter(role__role_type=Role.RoleType.CLIENT)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def providers(self, request):
        users = User.objects.filter(
            role__role_type=Role.RoleType.PROVIDER
        )
        serializer = ProviderScheduleSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], url_path='update-user')
    def update_user_profile(self, request, pk=None):
        try:
            user = get_object_or_404(
                User.objects.select_related('profile'),
                id=pk,
                deleted_at__isnull=True
            )
            
            user.name = request.data['name']
            user.email = request.data['email']
            user.cpf = request.data['cpf']
            user.profile.profile_picture = request.data['profile_picture']
            user.profile.street = request.data['street']
            user.profile.number = request.data['number']
            user.profile.city = request.data['city']
            user.profile.state = request.data['state']
            user.profile.zip_code = request.data['zip_code']
            
            user.profile.save()
            
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )            
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
class AuthenticationView(ViewSet):

    def list(self, request, *args, **kwargs):
        content = {'message': 'List of items'}
        return Response(content, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={'remove_password': True, 'remove_features': True})
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Credenciais inválidas!'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'user': serializer.data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciais inválidas!'}, status=status.HTTP_401_UNAUTHORIZED)

    
    @action(detail=False, methods=['post'], url_path='reset-password-request')
    def reset_password_request(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = get_random_string(length=32)  # Crie um token único
            reset_url = request.build_absolute_uri(reverse('reset-password-confirm', kwargs={'token': token}))
            
            user.password_reset_token = token
            user.save()
            
            send_mail(
                'Redefinição de Senha',
                f'Você recebeu este e-mail porque solicitou a redefinição da sua senha. Clique no link para redefinir sua senha: {reset_url}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({'message': 'E-mail de redefinição de senha enviado.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='reset-password-confirm/(?P<token>[^/.]+)')
    def reset_password_confirm(self, request, token=None):
        new_password = request.data.get('new_password')
        try:
            # Aqui você deve validar o token contra o que você armazenou anteriormente
            # Se o token for válido, continue. Caso contrário, retorne um erro.

            user = User.objects.get(
                password_reset_token=token,    
            )  # Obtenha o usuário de acordo com a lógica de validação do token
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Senha atualizada com sucesso.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    pass

class CustomTokenRefreshView(TokenRefreshView):
    pass

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)