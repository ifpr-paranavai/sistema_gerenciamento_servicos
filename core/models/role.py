from django.db import models
from core.models.mixins import TimeStampedModel
from core.models.feature import Feature

class Role(TimeStampedModel):
    class RoleType(models.TextChoices):
        CLIENT = 'client'
        PROVIDER = 'provider'
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    features = models.ManyToManyField(Feature, related_name='roles')
    role_type = models.CharField(max_length=10, choices=RoleType.choices, default=RoleType.CLIENT)

    def __str__(self):
        return self.name
