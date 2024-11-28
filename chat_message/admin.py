from django.contrib import admin
from chat_message.models import Message, Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'participants_list', 'created_at')
    search_fields = ('participants__name',)
    list_filter = ('created_at',)

    def participants_list(self, obj):
        return ", ".join([user.name for user in obj.participants.all()])
    participants_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'content_snippet', 'timestamp')
    search_fields = ('chat__id', 'sender__name', 'content')
    list_filter = ('timestamp',)

    def content_snippet(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Message Preview'
