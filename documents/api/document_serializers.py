import base64
from rest_framework import serializers

from documents.models.document import Document

class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_content = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size', 'document_type', 'file_content', 'created_at', 'updated_at']
        read_only_fields = ['file_name', 'file_type', 'file_content', 'file_size', 'created_at', 'updated_at']

    def get_file_content(self, obj):
        if obj.file_content:
            return base64.b64encode(obj.file_content).decode('utf-8')
        return None

    def create(self, validated_data):
        file = validated_data.pop('file', None)
        if not file:
            raise serializers.ValidationError({'file': 'Arquivo é obrigatório'})

        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']:
            raise serializers.ValidationError({'file': 'Tipo de arquivo não permitido'})

        # Lê o arquivo e cria o documento
        file_content = file.read()
        document = Document.objects.create(
            file_name=file.name,
            file_content=file_content,
            file_type=file_extension,
            file_size=file.size,
            document_type=validated_data.get('document_type')
        )
        return document