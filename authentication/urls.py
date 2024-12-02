from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.api.views import AuthenticationView, CustomTokenObtainPairView, CustomTokenRefreshView


router = DefaultRouter()
router.register(r'', AuthenticationView, basename='autenticacao')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password-confirm/<str:token>/', 
         AuthenticationView.as_view({'post': 'reset_password_confirm'}), 
         name='reset-password-confirm'),
    path('', include(router.urls)),
]