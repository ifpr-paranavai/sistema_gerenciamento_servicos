from django.urls import path, include
from chat_message.api.views import ChatMessageView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ChatMessageView, basename='chat')


urlpatterns = [
    path('', include(router.urls)),
]
