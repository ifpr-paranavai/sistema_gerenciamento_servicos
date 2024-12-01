from django.db import models
import uuid
from django.db.models import Q
from datetime import datetime, timedelta

from django.forms import ValidationError
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
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='client_appointments')
    provider = models.ForeignKey(User, on_delete=models.PROTECT, related_name='provider_appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    is_completed = models.BooleanField(default=False)
    documents = models.ManyToManyField(Document, related_name='appointments')
    observation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at'] 

    def __str__(self):
        return f"Appointment {self.id} for {self.client.name} with {self.provider.name}"

    def delete(self, using=None, keep_parents=False):
        if self.status != self.Status.PENDING:
            raise ValidationError("Este agendamento não pode ser excluído pois já foi confirmado.")
        return super().delete()
    
    @classmethod
    def check_availability(cls, proposed_date, provider_id, service_duration, exclude_appointment_id=None):
        """
        Verifica se o horário está disponível para agendamento
        
        Args:
            proposed_date: Data/hora proposta para o agendamento
            provider_id: ID do prestador
            service_duration: Duração do serviço em minutos
            exclude_appointment_id: ID do agendamento a ser excluído da verificação (para updates)
        """
        if isinstance(proposed_date, str):
            proposed_date = datetime.fromisoformat(proposed_date.replace('Z', '+00:00'))

        service_end = proposed_date + timedelta(minutes=service_duration)

        base_query = cls.objects.filter(
            provider_id=provider_id,
            deleted_at__isnull=True,
            status__in=[cls.Status.PENDING, cls.Status.IN_PROGRESS]
        )

        if exclude_appointment_id:
            base_query = base_query.exclude(id=exclude_appointment_id)

        conflicting_appointments = base_query.filter(
            Q(appointment_date__lt=service_end) &
            Q(appointment_date__gt=proposed_date - timedelta(minutes=60))
        )

        conflicts = []
        for app in conflicting_appointments:
            app_duration = app.services.first().duration if app.services.exists() else 0
            app_end = app.appointment_date + timedelta(minutes=app_duration)
            
            if (app.appointment_date <= service_end and 
                app_end >= proposed_date):
                conflicts.append({
                    'appointment_id': app.id,
                    'start': app.appointment_date,
                    'end': app_end,
                    'service': app.services.first().name if app.services.exists() else 'Não especificado',
                    'client': app.client.name,
                    'status': app.status
                })

        return {
            'is_available': len(conflicts) == 0,
            'conflicts': conflicts,
            'proposed_start': proposed_date,
            'proposed_end': service_end
        }