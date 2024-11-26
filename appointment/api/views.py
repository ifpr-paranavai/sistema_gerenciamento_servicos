from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from appointment.models import Appointment, Review
from appointment.api.serializers import AppointmentSerializer, ReviewSerializer
from core.models.mixins import DynamicPermissionModelViewSet

class AppointmentViewSet(DynamicPermissionModelViewSet):
    queryset = Appointment.objects.filter(deleted_at__isnull=True).all()
    serializer_class = AppointmentSerializer
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Atualiza o status de um agendamento específico
        """
        try:
            appointment = self.get_object()
            new_status = request.data.get('status')
            
            if request.user.role.role_type != 'provider' or appointment.provider != request.user:
                return Response(
                    {'error': 'Você não tem permissão para alterar este agendamento'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if not new_status:
                return Response(
                    {'error': 'Status não fornecido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            appointment.status = new_status
            appointment.save()
            
            serializer = self.get_serializer(appointment)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ReviewViewSet(DynamicPermissionModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
