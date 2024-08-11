from rest_framework import viewsets
from appointment.models import Appointment, Review
from appointment.api.serializers import AppointmentSerializer, ReviewSerializer
from authentication.permissions.decorator import permission_required

# @permission_required('pode_ver_relatorios')
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
