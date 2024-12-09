from typing import List
from django.db.models import Q, Count
from .models import Message, Chat

class MessageService:
    @staticmethod
    def get_unread_messages_count(user_id: int) -> int:
        return Message.objects.filter(
            chat__participants__id=user_id,
            vizualized=False
        ).exclude(sender_id=user_id).count()
    
    @staticmethod
    def mark_messages_as_read(chat_id: int, user_id: int) -> None:
        Message.objects.filter(
            chat_id=chat_id,
            vizualized=False
        ).exclude(sender_id=user_id).update(vizualized=True)