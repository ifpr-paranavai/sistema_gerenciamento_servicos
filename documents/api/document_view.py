from rest_framework import status
from rest_framework.response import Response
from core.models.mixins import DynamicPermissionModelViewSet
from documents.models.document import Document
from .document_serializers import DocumentSerializer


class DocumentViewSet(DynamicPermissionModelViewSet):
    queryset = Document.objects.filter(deleted_at=None)
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'error': 'Nenhum arquivo enviado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Valida a extensão do arquivo
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']:
                return Response(
                    {'error': 'Tipo de arquivo não permitido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            document_type = request.data.get('document_type')
            if not document_type:
                return Response(
                    {'error': 'Tipo de documento é obrigatório'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Lê o arquivo e salva no banco
            file_content = file.read()
            document = Document.objects.create(
                file_name=file.name,
                file_content=file_content,
                file_type=file_extension,
                file_size=file.size,
                document_type=document_type
            )

            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            