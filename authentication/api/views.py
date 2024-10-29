import bcrypt
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.api.serializers import SimpleUserSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from authentication.models import User
from core.models.mixins import DynamicViewPermissions
from core.models.profile import Profile

class UserViewSet(ViewSet):
    permission_classes = [DynamicViewPermissions]
    serializer_class = SimpleUserSerializer

    @action(detail=False, methods=['get'])
    def clients(self, request):
        users = User.objects.filter(profile__profile_type=Profile.ProfileType.CLIENT)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def providers(self, request):
        users = User.objects.filter(profile__profile_type=Profile.ProfileType.PROVIDER)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data)

class AuthenticationView(ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        content = {'message': 'List of items'}
        return Response(content, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        content = {'message': f'Item with id {pk}'}
        return Response(content, status=status.HTTP_200_OK)

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