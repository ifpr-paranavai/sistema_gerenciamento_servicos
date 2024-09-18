from core.models.mixins import DynamicPermissionModelViewSet
from service.models import Service
from service.api.serializers import ServiceSerializer

class ServiceViewSet(DynamicPermissionModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
