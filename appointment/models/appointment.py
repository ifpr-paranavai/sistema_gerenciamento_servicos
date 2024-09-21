from django.db import models
import uuid
from authentication.models import User
from service.models import Service
from core.models.mixins import TimeStampedModel

class Appointment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=100)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_appointments')
    services = models.ManyToManyField(Service)
    is_completed = models.BooleanField(default=False)

