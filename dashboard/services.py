from datetime import datetime
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from appointment.models.appointment import Appointment
from service.models.service import Service


class DateValidationService:
    """Serviço para validação de datas."""
    @staticmethod
    def validate_date_range(start_date, end_date):
        if (start_date and not end_date) or (end_date and not start_date):
            raise ValueError('Both startDate and endDate must be provided together')
        try:
            start = datetime.fromisoformat(start_date) if start_date else None
            end = datetime.fromisoformat(end_date) if end_date else None
            return start, end
        except ValueError:
            raise ValueError("Invalid date format")


class DashboardDataService:
    """Serviço para manipulação de dados do dashboard."""
    @staticmethod
    def get_filtered_appointments(start_date=None, end_date=None):
        """Filtra agendamentos por período e remove deletados."""
        appointments = Appointment.objects.filter(
            deleted_at__isnull=True,
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True
        )
        if start_date and end_date:
            appointments = appointments.filter(appointment_date__range=(start_date, end_date))
        return appointments

    @staticmethod
    def calculate_service_stats(appointments):
        """Calcula estatísticas de serviços agrupadas por mês."""
        stats = appointments.filter(
            status=Appointment.Status.COMPLETED,
            deleted_at__isnull=True,
            services__deleted_at__isnull=True
        ).annotate(
            month=TruncMonth('appointment_date')
        ).values(
            'services__name', 'month'
        ).annotate(
            totalValue=Sum('services__cost'),
            quantity=Count('id')
        ).order_by('services__name', 'month')

        return [
            {
                'serviceName': stat['services__name'],
                'date': stat['month'],
                'totalValue': stat['totalValue'] or 0,
                'quantity': stat['quantity'],
                'averageValue': (stat['totalValue'] / stat['quantity']) if stat['quantity'] > 0 else 0
            }
            for stat in stats if stat['services__name']
        ]

    @staticmethod
    def calculate_total_revenue(appointments):
        """Calcula a receita total de agendamentos concluídos."""
        completed_appointments = appointments.filter(
            status=Appointment.Status.COMPLETED,
            deleted_at__isnull=True
        ).prefetch_related('services')
        return sum([
            sum([service.cost for service in app.services.filter(deleted_at__isnull=True)])
            for app in completed_appointments
        ])
