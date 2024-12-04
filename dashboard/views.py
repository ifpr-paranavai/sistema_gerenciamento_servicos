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
from dashboard.services import DashboardDataService, DateValidationService
from service.models.service import Service
from .serializers import DashboardStatSerializer

class DashboardStatsView(ViewSet):
    """
    ViewSet para gerenciar estatísticas do dashboard.
    """
    permission_classes = [DynamicViewPermissions]

    @swagger_auto_schema(
        operation_description="Get dashboard statistics",
        manual_parameters=[
            openapi.Parameter(
                'startDate', openapi.IN_QUERY, description="Start date (ISO format)",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False
            ),
            openapi.Parameter(
                'endDate', openapi.IN_QUERY, description="End date (ISO format)",
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, required=False
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
        - Receita total
        - Estatísticas por serviço
        - Agendamentos atuais
        - Próximos agendamentos
        """
        try:
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')

            # Validar datas
            start, end = DateValidationService.validate_date_range(start_date, end_date)

            # Obter dados do dashboard
            appointments = DashboardDataService.get_filtered_appointments(start, end)
            dashboard_data = {
                'totalRevenue': DashboardDataService.calculate_total_revenue(appointments),
                'serviceStats': DashboardDataService.calculate_service_stats(appointments),
                'currentAppointments': appointments.filter(
                    status=Appointment.Status.IN_PROGRESS
                ).order_by('appointment_date')[:5],
                'upcomingAppointments': appointments.filter(
                    appointment_date__gte=timezone.now(),
                    status=Appointment.Status.PENDING
                ).order_by('appointment_date')[:5]
            }

            # Serializar e retornar
            serializer = DashboardStatSerializer(dashboard_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
