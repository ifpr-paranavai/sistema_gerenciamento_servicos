from rest_framework import viewsets
from appointment.models import Appointment, Review
from appointment.api.serializers import AppointmentSerializer, ReviewSerializer
from core.models.mixins import DynamicPermissionModelViewSet

class AppointmentViewSet(DynamicPermissionModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class ReviewViewSet(DynamicPermissionModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
