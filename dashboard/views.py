from datetime import datetime
from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from appointment.models.appointment import Appointment
from core.models.mixins import DynamicViewPermissions
from service.models.service import Service
from .serializers import DashboardStatSerializer

class DashboardStatsView(ViewSet):
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
           
       # Estatísticas por serviço
       service_stats = self._get_service_stats(appointments)

       # Agendamentos atuais
       current_appointments = appointments.filter(
           status='IN_PROGRESS'
       ).select_related(
           'client',
           'provider'
       ).prefetch_related(
           'services'
       ).order_by('appointment_date')[:5]

       # Próximos agendamentos
       now = timezone.now()
       upcoming_appointments = appointments.filter(
           appointment_date__gte=now,
           status__in=['SCHEDULED', 'IN_PROGRESS']
       ).select_related(
           'client',
           'provider'
       ).prefetch_related(
           'services'
       ).order_by('appointment_date')[:5]

       # Total de agendamentos concluídos como 'revenue'
       total_revenue = appointments.filter(
           status='COMPLETED'
       ).count()

       return {
           'totalRevenue': total_revenue,
           'serviceStats': service_stats,
           'currentAppointments': current_appointments,
           'upcomingAppointments': upcoming_appointments
       }

   def _get_filtered_appointments(self, start_date=None, end_date=None):
       """
       Filtra os agendamentos por período
       """
       appointments = Appointment.objects.all()
       
       if start_date and end_date:
           try:
               start = datetime.fromisoformat(start_date)
               end = datetime.fromisoformat(end_date)
               appointments = appointments.filter(appointment_date__range=(start, end))
           except ValueError:
               raise ValueError("Invalid date format")
               
       return appointments

   def _get_service_stats(self, appointments):
       """
       Calcula estatísticas por serviço
       """
       return Service.objects.annotate(
           totalValue=Count(
               'appointments',
               filter=appointments.filter(
                   status='COMPLETED'
               )
           )
       ).values('id', 'name', 'totalValue')

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
           Appointment.objects.first()
           Service.objects.first()
           
           return Response(
               {"status": "healthy"},
               status=status.HTTP_200_OK
           )
       except Exception as e:
           return Response(
               {"status": "unhealthy", "error": str(e)},
               status=status.HTTP_500_INTERNAL_SERVER_ERROR
           )