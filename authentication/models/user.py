import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from core.models.profile import Profile
from core.models.feature import Feature
from core.models.role import Role
from core.models.mixins import TimeStampedModel

class User(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True)
    name = models.CharField(max_length=155)
    password = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    features = models.ManyToManyField(Feature, related_name='system_users')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_') and not self.password.startswith('$2b$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_permission(self, permission_name):
        return self.features.filter(name=permission_name).exists() or \
               (self.role and self.role.features.filter(name=permission_name).exists())