from django.shortcuts import get_object_or_404
from authentication.models.user import User
from chat_message.api.serializers import ChatUserSerializer
from chat_message.models import Chat, Message
from chat_message.services import MessageService
from core.models.mixins import DynamicPermissionModelViewSet
from authentication.api.serializers import SimpleUserSerializer
from core.models.mixins import DynamicViewPermissions
from rest_framework.response import Response
from rest_framework.decorators import action



class ChatMessageView(DynamicPermissionModelViewSet):
    permission_classes = [DynamicViewPermissions]
    serializer_class = SimpleUserSerializer
    
    @action(detail=False, methods=["get"])
    def list_user_chats(self, request):
        user = request.user
        chats = Chat.objects.filter(participants=user)

        chat_data = []
        for chat in chats:
            messages = chat.messages.order_by("timestamp")

            my_messages = []
            other_messages = []

            for message in messages:
                if message.sender == user:
                    my_messages.append({
                        "id": message.id,
                        "content": message.content,
                        "timestamp": message.timestamp,
                    })
                else:
                    other_messages.append({
                        "id": message.id,
                        "sender_name": message.sender.name,
                        "content": message.content,
                        "timestamp": message.timestamp,
                    })

            participants = chat.participants.exclude(id=user.id)
            serialized_participants = ChatUserSerializer(participants, many=True).data

            chat_data.append({
                "chat_id": chat.id,
                "participants": serialized_participants,
                "created_at": chat.created_at,
                "my_messages": my_messages,
                "other_messages": other_messages,
            })

        return Response(chat_data)
        
    
    @action(detail=True, methods=["post"])
    def create_or_get_chat(self, request, pk=None):
        user_sender = request.user
        user_receiver_id = pk

        if not user_receiver_id:
            return Response({"error": "user_id é obrigatório."}, status=400)

        user_receiver = get_object_or_404(User, id=user_receiver_id)

        chat = Chat.objects.filter(participants=user_sender).filter(
            participants=user_receiver).first()
        
        if not chat:
            chat = Chat.objects.create()
            chat.participants.add(user_sender, user_receiver)

        return Response({
            "chat_id": chat.id,
            "participants": ChatUserSerializer(chat.participants.all(), many=True).data,
        })


    @action(detail=True, methods=["get"])
    def list_messages(self, request, pk=None):
        user = request.user
        messages = Message.objects.filter(chat__id=pk).order_by("timestamp")

        my_messages = []
        other_messages = []

        for message in messages:
            if message.sender == user:
                my_messages.append({
                    "id": message.id,
                    "content": message.content,
                    "timestamp": message.timestamp,
                })
            else:
                other_messages.append({
                    "id": message.id,
                    "sender_name": message.sender.name,
                    "content": message.content,
                    "timestamp": message.timestamp,
                })

        return Response({
            "my_messages": my_messages,
            "other_messages": other_messages,
        })


    @action(detail=False, methods=["post"])
    def send_message(self, request):
        chat_id = request.data.get("chat_id")
        content = request.data.get("content")

        if not chat_id or not content:
            return Response({"error": "chat_id e content são obrigatórios."}, status=400)

        chat = get_object_or_404(Chat, id=chat_id)
        sender = request.user

        if sender not in chat.participants.all():
            return Response({"error": "Você não faz parte deste chat."}, status=403)

        message = Message.objects.create(
            chat=chat, sender=sender, content=content)

        return Response({
            "message_id": message.id,
            "content": message.content,
            "timestamp": message.timestamp,
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = MessageService.get_unread_messages_count(request.user.id)
        return Response({'count': count})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        MessageService.mark_messages_as_read(pk, request.user.id)
        return Response({'message': 'Messages marked as read.'})