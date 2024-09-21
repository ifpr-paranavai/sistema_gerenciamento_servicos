from rest_framework import serializers

from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement

class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'file_types', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ServiceDocumentRequirementSerializer(serializers.ModelSerializer):
    document_template = DocumentTemplateSerializer(read_only=True)

    class Meta:
        model = ServiceDocumentRequirement
        fields = ['id', 'service', 'document_template', 'is_required', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']