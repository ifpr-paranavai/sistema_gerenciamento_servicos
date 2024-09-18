from django.db import models
from core.models.mixins import TimeStampedModel

class Service(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
