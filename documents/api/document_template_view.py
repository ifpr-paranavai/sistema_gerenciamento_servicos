from core.models.mixins import DynamicPermissionModelViewSet
from documents.api.document_template_serializers import DocumentTemplateSerializer, ServiceDocumentRequirementSerializer
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core.models.mixins import DynamicPermissionModelViewSet
from documents.models.document_template import DocumentTemplate
from .document_template_serializers import DocumentTemplateSerializer

class DocumentTemplateViewSet(DynamicPermissionModelViewSet):
    queryset = DocumentTemplate.objects.filter(deleted_at=None)
    serializer_class = DocumentTemplateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        return Response(serializer.data)

class ServiceDocumentRequirementViewSet(DynamicPermissionModelViewSet):
    queryset = ServiceDocumentRequirement.objects.all()
    serializer_class = ServiceDocumentRequirementSerializer