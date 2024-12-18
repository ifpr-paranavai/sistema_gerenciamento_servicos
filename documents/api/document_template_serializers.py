import json
import base64
import mimetypes
from rest_framework import serializers
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement
from documents.models.document import Document

class DocumentTemplateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False, allow_null=True, allow_empty_file=True)
    document = serializers.SerializerMethodField()
    file_types = serializers.SerializerMethodField()
    file_types_write = serializers.CharField(write_only=True, required=False, source='file_types')

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'file_types', 'file_types_write',
                 'document', 'file', 'created_at', 'updated_at']
        read_only_fields = ['document', 'created_at', 'updated_at']
    
    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            data = data.dict()

        # Tratamento do file
        if 'file' in data:
            if not data['file'] or data['file'] == 'null' or data['file'] == '':
                data.pop('file')

        # Garantir que file_types seja mantido
        if 'file_types' in data:
            initial_data = data['file_types']
            try:
                # Se já é uma string JSON válida, mantém como está
                if isinstance(initial_data, str):
                    json.loads(initial_data)  # Valida se é JSON válido
                    data['file_types'] = initial_data
                else:
                    # Se não for string, converte para JSON
                    data['file_types'] = json.dumps(initial_data)
            except json.JSONDecodeError:
                # Se não for JSON válido, mantém o valor original para ser validado depois
                data['file_types'] = initial_data

        result = super().to_internal_value(data)
        return result

    def validate_file_types(self, value):
        """Valida e normaliza file_types"""
        try:
            file_types = json.loads(value) if isinstance(value, str) else value
            if isinstance(file_types, list):
                normalized = []
                for ft in file_types:
                    if isinstance(ft, str):
                        normalized.extend([ext.strip().lower() for ext in ft.split(',') if ext.strip()])
                return json.dumps(list(dict.fromkeys(normalized)))
        except json.JSONDecodeError:
            pass
        
        raise serializers.ValidationError("Formato inválido para file_types")

    def create(self, validated_data):
        file = validated_data.pop('file', None)
        document = None

        if file:
            try:
                from documents.models.document import Document
                document = Document.objects.create(
                    file_name=file.name,
                    file_content=file.read(),
                    file_type=file.name.split('.')[-1].lower(),
                    document_type='start'
                )
            except Exception as e:
                raise serializers.ValidationError(f'Erro ao salvar arquivo: {str(e)}')

        try:
            template = DocumentTemplate.objects.create(
                **validated_data,
                document=document
            )

            return template
        except Exception as e:
            if document:
                document.delete()
            raise serializers.ValidationError(f'Erro ao salvar template: {str(e)}')

    def update(self, instance, validated_data):
        file = validated_data.pop('file', None)
        if file:
            try:
                if instance.document:
                    instance.document.file_name = file.name
                    instance.document.file_content = file.read()
                    instance.document.file_type = file.name.split('.')[-1].lower()
                    instance.document.save()
                else:
                    from documents.models.document import Document
                    document = Document.objects.create(
                        file_name=file.name,
                        file_content=file.read(),
                        file_type=file.name.split('.')[-1].lower(),
                        document_type='start'
                    )
                    instance.document = document
            except Exception as e:
                raise serializers.ValidationError(f'Erro ao salvar arquivo: {str(e)}')

        for attr, value in validated_data.items():
            if attr != 'file':
                setattr(instance, attr, value)
        
        instance.save()
        return instance

    def get_document(self, obj):
        try:
            if not obj.document or not obj.document.file_content:
                return None

            mime_type, _ = mimetypes.guess_type(obj.document.file_name)
            if not mime_type:
                mime_type = f'application/{obj.document.file_type}'

            base64_content = base64.b64encode(obj.document.file_content).decode('utf-8')
            
            return {
                'name': obj.document.file_name,
                'type': mime_type,
                'lastModified': int(obj.document.updated_at.timestamp() * 1000),
                'size': len(obj.document.file_content),
                'dataUrl': f'data:{mime_type};base64,{base64_content}'
            }
        except Exception:
            return None
        
    def get_file_types(self, obj):
        try:
            return obj.file_types.split(',')
        except json.JSONDecodeError:
            return []

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