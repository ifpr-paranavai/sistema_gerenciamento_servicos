from django.db import models
from core.models.mixins import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator

from service.models.service import Service

class Review(TimeStampedModel):
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return f'Review for {self.service.name} by {self.user.username}'