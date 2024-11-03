from rest_framework import serializers

from documents.api.document_serializers import DocumentSerializer
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement

class DocumentTemplateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)
    document = DocumentSerializer(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'file_types', 'document', 'file', 'created_at', 'updated_at']
        read_only_fields = ['document', 'created_at', 'updated_at']

    def create(self, validated_data):
        file = validated_data.pop('file', None)
        if not file:
            raise serializers.ValidationError({'file': 'Arquivo é obrigatório'})

        file_extension = file.name.split('.')[-1].lower()
        allowed_extensions = validated_data.get('file_types', '').split(',')
        
        if file_extension not in [ext.strip() for ext in allowed_extensions]:
            raise serializers.ValidationError({
                'file': f'Tipo de arquivo não permitido. Tipos permitidos: {validated_data.get("file_types")}'
            })

        try:
            # Criar o Document primeiro
            from documents.models.document import Document
            document = Document.objects.create(
                file_name=file.name,
                file_content=file.read(),
                file_type=file_extension,
                document_type='start'  # ou você pode adicionar um campo para definir isso
            )

            # Criar o DocumentTemplate com o Document associado
            template = DocumentTemplate.objects.create(
                **validated_data,
                document=document
            )

            return template
        except Exception as e:
            raise serializers.ValidationError(f'Erro ao salvar template: {str(e)}')

    def update(self, instance, validated_data):
        file = validated_data.pop('file', None)
        if file:
            file_extension = file.name.split('.')[-1].lower()
            allowed_extensions = validated_data.get('file_types', instance.file_types).split(',')
            
            if file_extension not in [ext.strip() for ext in allowed_extensions]:
                raise serializers.ValidationError({
                    'file': f'Tipo de arquivo não permitido. Tipos permitidos: {validated_data.get("file_types", instance.file_types)}'
                })

            # Atualizar o Document existente ou criar um novo
            if instance.document:
                instance.document.file_name = file.name
                instance.document.file_content = file.read()
                instance.document.file_type = file_extension
                instance.document.save()
            else:
                from documents.models.document import Document
                document = Document.objects.create(
                    file_name=file.name,
                    file_content=file.read(),
                    file_type=file_extension,
                    document_type='start'
                )
                instance.document = document

        for attr, value in validated_data.items():
            if attr != 'file':
                setattr(instance, attr, value)
        
        instance.save()
        return instance
    

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