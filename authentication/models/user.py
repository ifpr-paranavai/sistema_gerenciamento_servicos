import uuid
import bcrypt
from django.db import models
from core.models.profile import Profile
from core.models.feature import Feature
from core.models.role import Role
from core.models.mixins import TimeStampedModel

class User(TimeStampedModel):
    id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False
    )
    email = models.EmailField(
        verbose_name='Email Address', max_length=255, unique=True
    )
    name = models.CharField(max_length=155)
    password = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    profile = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True
    )
    features = models.ManyToManyField(Feature, related_name='users')

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.password:
            password_bytes = self.password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            self.password = hashed_password.decode('utf-8')
        super().save(*args, **kwargs)
    
    def has_permission(self, permission_name):
        return self.features.filter(name=permission_name).exists()
        