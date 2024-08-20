from django.db import models
from core.models.mixins import TimeStampedModel
from core.models.feature import Feature

class Role(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    features = models.ManyToManyField(Feature, related_name='roles')

    def __str__(self):
        return self.name
