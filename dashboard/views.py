from datetime import datetime
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models.functions import TruncMonth

from appointment.models.appointment import Appointment
from core.models.mixins import DynamicViewPermissions
from service.models.service import Service
from .serializers import DashboardStatSerializer


class DashboardStatsView(ViewSet):
    """
    ViewSet para gerenciar estatísticas do dashboard
    """
    permission_classes = [DynamicViewPermissions]

    @swagger_auto_schema(
        operation_description="Get dashboard statistics",
        manual_parameters=[
            openapi.Parameter(
                'startDate',
                openapi.IN_QUERY,
                description="Start date (ISO format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                required=False
            ),
            openapi.Parameter(
                'endDate',
                openapi.IN_QUERY,
                description="End date (ISO format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                required=False
            ),
        ],
        responses={
            200: DashboardStatSerializer,
            400: 'Bad Request - Invalid date format or missing date parameter',
            500: 'Internal Server Error'
        }
    )
    def list(self, request):
        """
        Retorna estatísticas do dashboard incluindo:
        - Total de agendamentos concluídos
        - Estatísticas por serviço
        - Agendamentos atuais
        - Próximos agendamentos
        """
        try:
            # Pegar parâmetros da query
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')

            # Validação das datas
            if (start_date and not end_date) or (end_date and not start_date):
                return Response(
                    {'error': 'Both startDate and endDate must be provided together'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Carregar dados do dashboard
            dashboard_data = self._get_dashboard_data(start_date, end_date)

            # Serializar e retornar
            serializer = DashboardStatSerializer(dashboard_data)
            return Response(serializer.data)

        except ValueError as e:
            return Response(
                {'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:mm:ss)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_dashboard_data(self, start_date=None, end_date=None):
        """
        Obtém todos os dados necessários para o dashboard
        """
        appointments = self._get_filtered_appointments(start_date, end_date)

        # Estatísticas por serviço agrupadas por mês
        service_stats = self._get_service_stats(appointments)

        # Agendamentos atuais - ativos
        current_appointments = appointments.filter(
            status=Appointment.Status.IN_PROGRESS,
            deleted_at__isnull=True
        ).select_related(
            'client',
            'provider'
        ).prefetch_related(
            'services'
        ).filter(
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True,
            services__deleted_at__isnull=True
        ).order_by('appointment_date')[:5]

        # Próximos agendamentos - ativos
        now = timezone.now()
        upcoming_appointments = appointments.filter(
            appointment_date__gte=now,
            status__in=[Appointment.Status.PENDING],
            deleted_at__isnull=True
        ).select_related(
            'client',
            'provider'
        ).prefetch_related(
            'services'
        ).filter(
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True,
            services__deleted_at__isnull=True
        ).order_by('appointment_date')[:5]

        # Total revenue apenas de itens ativos
        completed_appointments = appointments.filter(
            status=Appointment.Status.COMPLETED,
            deleted_at__isnull=True,
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True,
            services__deleted_at__isnull=True
        ).prefetch_related('services')

        total_revenue = sum([
            sum([service.cost for service in app.services.filter(deleted_at__isnull=True)])
            for app in completed_appointments
        ])

        return {
            'totalRevenue': total_revenue,
            'serviceStats': service_stats,
            'currentAppointments': current_appointments,
            'upcomingAppointments': upcoming_appointments
        }

    def _get_filtered_appointments(self, start_date=None, end_date=None):
        """
        Filtra os agendamentos por período e remove deletados
        """
        appointments = Appointment.objects.filter(
            deleted_at__isnull=True
        ).filter(
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True
        )

        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                appointments = appointments.filter(
                    appointment_date__range=(start, end)
                )
            except ValueError:
                raise ValueError("Invalid date format")

        return appointments

    def _get_service_stats(self, appointments):
        """
        Calcula estatísticas por serviço agrupadas por mês,
        excluindo itens deletados
        """
        # Primeiro, agrupa os agendamentos por serviço e mês
        stats = appointments.filter(
            status=Appointment.Status.COMPLETED,
            deleted_at__isnull=True,
            services__deleted_at__isnull=True  # Exclui serviços deletados
        ).annotate(
            month=TruncMonth('appointment_date')
        ).values(
            'services__name',
            'month'
        ).annotate(
            totalValue=Sum('services__cost'),
            quantity=Count('id')
        ).values(
            'services__name',
            'month',
            'totalValue',
            'quantity'
        ).filter(  # Garante que todos os relacionamentos estão ativos
            services__deleted_at__isnull=True,
            client__deleted_at__isnull=True,
            provider__deleted_at__isnull=True
        ).order_by('services__name', 'month')

        # Formata os dados para o serializer
        formatted_stats = []
        for stat in stats:
            if stat['services__name']:  # Verifica se o nome do serviço não é nulo
                formatted_stats.append({
                    'serviceName': stat['services__name'],
                    'date': stat['month'],
                    'totalValue': stat['totalValue'] or 0,
                    'quantity': stat['quantity'],
                    'averageValue': (stat['totalValue'] / stat['quantity']) 
                                  if stat['quantity'] > 0 else 0
                })

        return formatted_stats

    @swagger_auto_schema(
        operation_description="Health check for dashboard API",
        responses={
            200: "API is healthy",
            500: "API is not healthy"
        }
    )
    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Endpoint para verificar a saúde da API do dashboard
        """
        try:
            # Verificar se pode acessar o banco de dados
            # Usando filter para não trazer itens deletados
            Appointment.objects.filter(deleted_at__isnull=True).first()
            Service.objects.filter(deleted_at__isnull=True).first()
            
            return Response(
                {"status": "healthy"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status": "unhealthy", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )