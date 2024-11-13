from typing import List
from django.core.files.uploadedfile import UploadedFile
from documents.models.document import Document
from rest_framework import serializers

class DocumentService:
    @staticmethod
    def validate_file_type(file: UploadedFile, allowed_types: List[str]) -> None:
        extension = file.name.split('.')[-1].lower()
        if isinstance(allowed_types, str):
            allowed_types = eval(allowed_types)
            
        if extension not in allowed_types:
            raise serializers.ValidationError(
                f'Tipo de arquivo inválido. Tipos permitidos: {", ".join(allowed_types)}'
            )

    @staticmethod
    def create_document(file: UploadedFile) -> Document:
        try:

            if not file.size or file.size <= 0:
                raise serializers.ValidationError("Arquivo vazio ou inválido")

            file.seek(0)
            content = file.read()
            
            if content == b'undefined' or len(content) < 10:
                raise serializers.ValidationError(
                    "Conteúdo do arquivo inválido ou corrompido"
                )

            document = Document(
                file_name=file.name,
                file_type=file.content_type.split('/')[1],
                file_size=len(content),
                document_type='start',
                file_content=content
            )
            
            document.save()
            return document
            
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao salvar documento: {str(e)}")