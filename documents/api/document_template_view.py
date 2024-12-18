import json
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
        data = self._format_data(request.data)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            headers=headers
        )
    
    def _format_data(self, data):
        """Helper method to format request data"""
        formatted_data = data.copy()
        
        # Format file_types
        if 'file_types' in formatted_data:
            file_types = formatted_data.getlist('file_types')[0]  # Pega o primeiro item da lista
            try:
                # Converte string JSON para lista Python
                file_types_list = json.loads(file_types)
                # Converte lista Python para string com elementos separados por vírgula
                formatted_data['file_types_write'] = ','.join(file_types_list)
                # Remove o campo original file_types
                del formatted_data['file_types']
            except json.JSONDecodeError:
                pass
                
        return formatted_data

class ServiceDocumentRequirementViewSet(DynamicPermissionModelViewSet):
    queryset = ServiceDocumentRequirement.objects.all()
    serializer_class = ServiceDocumentRequirementSerializer