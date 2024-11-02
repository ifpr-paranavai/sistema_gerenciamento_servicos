from rest_framework import serializers

from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement

class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'file_types', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ServiceDocumentRequirementSerializer(serializers.ModelSerializer):
    document_template = DocumentTemplateSerializer(read_only=True)
    document_template_id = serializers.PrimaryKeyRelatedField(
        source='document_template',
        queryset=DocumentTemplate.objects.all(),
        write_only=True
    )

    class Meta:
        model = ServiceDocumentRequirement
        fields = ['id', 'service', 'document_template', 'document_template_id', 'is_required', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'service', 'document_template']
        extra_kwargs = {
            'is_required': {'required': True}
        }