from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser

from core.models.mixins import DynamicPermissionModelViewSet
from documents.models.document import Document
from .document_serializers import DocumentSerializer

class DocumentViewSet(DynamicPermissionModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)