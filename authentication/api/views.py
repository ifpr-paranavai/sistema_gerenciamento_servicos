from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authentication.api.serializers import ProviderScheduleSerializer, SimpleUserSerializer, UserSerializer
from authentication.services import EmailService, UserService
from core.models.mixins import DynamicViewPermissions
from authentication.models import User
from core.models.role import Role


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
        users = User.objects.filter(role__role_type=Role.RoleType.PROVIDER)
        serializer = ProviderScheduleSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='update-user')
    def update_user_profile(self, request, pk=None):
        user = get_object_or_404(User.objects.select_related('profile'), id=pk, deleted_at__isnull=True)
        try:
            user = UserService.update_user(user, request.data)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AuthenticationView(ViewSet):
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                serializer = UserSerializer(user)
                return Response({
                    'user': serializer.data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='reset-password-request')
    def reset_password_request(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = UserService.generate_reset_password_token(user)
            EmailService.send_reset_password_email(user, token, request)
            return Response({'message': 'Reset password email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='reset-password-confirm/(?P<token>[^/.]+)')
    def reset_password_confirm(self, request, token=None):
        new_password = request.data.get('new_password')
        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(new_password)
            user.password_reset_token = None
            user.save()
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)


class CustomTokenObtainPairView(TokenObtainPairView):
    pass

class CustomTokenRefreshView(TokenRefreshView):
    pass