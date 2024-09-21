from core.models.mixins import DynamicPermissionModelViewSet
from documents.api.document_template_serializers import DocumentTemplateSerializer, ServiceDocumentRequirementSerializer
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement


class DocumentTemplateViewSet(DynamicPermissionModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer

class ServiceDocumentRequirementViewSet(DynamicPermissionModelViewSet):
    queryset = ServiceDocumentRequirement.objects.all()
    serializer_class = ServiceDocumentRequirementSerializer