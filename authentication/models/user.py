import uuid
import bcrypt
from django.db import models
from core.models.profile import Profile
from core.models.feature import Feature
from core.models.role import Role
from core.models.mixins import TimeStampedModel
from django.contrib.auth.hashers import make_password, check_password

class User(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True)
    name = models.CharField(max_length=155)
    password = models.CharField(max_length=255)  # Lembrar de usar hashing adequado
    cpf = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    features = models.ManyToManyField(Feature, related_name='system_users')
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if self.password:
            password_bytes = self.password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            self.password = hashed_password.decode('utf-8')
        super().save(*args, **kwargs)
        
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def has_permission(self, permission_name):
        return self.features.filter(name=permission_name).exists() or \
               (self.role and self.role.features.filter(name=permission_name).exists())

