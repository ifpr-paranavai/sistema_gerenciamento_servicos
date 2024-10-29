from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.api.views import UserViewSet


router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]