from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.api.views import AuthenticationView, CustomTokenObtainPairView, CustomTokenRefreshView


router = DefaultRouter()
router.register(r'', AuthenticationView, basename='autenticacao')

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),    
    path('', include(router.urls)),
]