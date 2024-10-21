from django.db import models
from appointment.models.appointment import Appointment
from authentication.models.user import User
from core.models.mixins import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator

from service.models.service import Service

class Review(TimeStampedModel):
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField()
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Review for {self.appointment.id} by {self.user.name}'