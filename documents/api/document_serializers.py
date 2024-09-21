from rest_framework import serializers

from documents.models.document import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'service', 'file', 'document_type', 'uploaded_at', 'filename', 'file_extension']
        read_only_fields = ['filename', 'file_extension', 'created_at', 'updated_at']