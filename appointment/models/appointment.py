from django.db import models
import uuid
from authentication.models import User
from documents.models.document import Document
from service.models import Service
from core.models.mixins import TimeStampedModel

class Appointment(TimeStampedModel):
    
    class Status(models.TextChoices):
        PENDING = 'Agendado'
        IN_PROGRESS = 'Em andamento'
        CANCELED = 'Cancelado'
        COMPLETED = 'Concluido'
        
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    is_completed = models.BooleanField(default=False)
    documents = models.ManyToManyField(Document, related_name='appointments', blank=True, null=True)

    def __str__(self):
        return f"Appointment {self.id} for {self.client.name} with {self.provider.name}"

    def delete(self, using=None, keep_parents=False):
        return super().delete()