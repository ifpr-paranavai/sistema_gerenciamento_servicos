from core.models.mixins import DynamicPermissionModelViewSet
from service.models import Service
from service.api.serializers import ServiceSerializer

class ServiceViewSet(DynamicPermissionModelViewSet):
    queryset = Service.objects.filter(deleted_at=None).prefetch_related(
        'document_requirements',
        'document_requirements__document_template'
    )
    serializer_class = ServiceSerializer
