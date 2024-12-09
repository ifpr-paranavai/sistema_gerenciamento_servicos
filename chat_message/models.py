
from django.db import models
from authentication.models.user import User


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between: {', '.join([user.name for user in self.participants.all()])}"


class Message(models.Model):
    chat = models.ForeignKey(
        Chat, on_delete=models.PROTECT, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.name} at {self.timestamp}"
