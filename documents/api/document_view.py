from argparse import Action

from rest_framework import status
from rest_framework.decorators import action
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
                document_type=document_type
            )

            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            document = self.get_object()
            response = HttpResponse(
                document.file_content,
                content_type=f'application/{document.file_type}'
            )
            response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        try:
            document = self.get_object()
            return Response({
                'file_name': document.file_name,
                'file_type': document.file_type,
                'content': base64.b64encode(document.file_content).decode('utf-8')
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )