from django.db import DataError
from django.test import TestCase
from core.models.feature import Feature
from core.models.role import Role
from documents.models.document import Document
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile



class DocumentModelTests(TestCase):
    
    def setUp(self):
        self.document = Document.objects.create(
            file_name="example.pdf",
            file_content=b"dummy_content",
            file_type="pdf",
            file_size=1024,
            document_type="start"
        )

    def test_document_creation(self):
        self.assertEqual(self.document.file_name, "example.pdf")
        self.assertEqual(self.document.file_type, "pdf")
        self.assertEqual(self.document.file_size, 1024)
        self.assertEqual(self.document.document_type, "start")
        self.assertEqual(str(self.document), "example.pdf - start")

    def test_file_extension_property(self):
        self.assertEqual(self.document.file_extension, "pdf")

    def test_invalid_document_type(self):
        with self.assertRaises(DataError):
            Document.objects.create(
                file_name="example.txt",
                file_content=b"dummy_content",
                file_type="txt",
                file_size=512,
                document_type="invalid"
            )



class DocumentViewSetTests(APITestCase):

    def setUp(self):
        self.url = reverse('document-list')

        # Criar Features necessárias para operações de documentos
        self.features = {
            "list": Feature.objects.get_or_create(name="documents.list_document", defaults={"description": "Pode listar documentos"})[0],
            "add": Feature.objects.get_or_create(name='documents.create_document', defaults={"description": "Pode adicionar documentos"})[0],
            "view": Feature.objects.get_or_create(name="documents.view_document", defaults={"description": "Pode visualizar documentos"})[0],
            "delete": Feature.objects.get_or_create(name="documents.destroy_document", defaults={"description": "Pode excluir documentos"})[0],
            "download": Feature.objects.get_or_create(name="documents.download_document", defaults={"description": "Pode fazer download de documentos"})[0],
            "preview": Feature.objects.get_or_create(name="documents.preview_document", defaults={"description": "Pode pré-visualizar documentos"})[0],
        }

        # Criar Role e associar as Features
        self.role = Role.objects.create(name="Document Manager", role_type="manager")
        self.role.features.set(self.features.values())

        # Criar usuário e associar o Role
        self.user = baker.make("authentication.User", role=self.role, is_active=True)
        self.user.save()

        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Criar documento inicial para os testes
        self.document = Document.objects.create(
            file_name="example.pdf",
            file_content=b"dummy_content",
            file_type="pdf",
            file_size=1024,
            document_type="start"
        )

    def test_list_documents(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_document_success(self):
        file = SimpleUploadedFile("new_doc.pdf", b"dummy_content", content_type="application/pdf")
        data = {
            "file": file,
            "document_type": "start"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 2)
        self.assertEqual(Document.objects.last().file_name, "example.pdf")

    def test_create_document_invalid_file_type(self):
        file = SimpleUploadedFile("new_doc.exe", b"dummy_content", content_type="application/exe")
        data = {
            "file": file,
            "document_type": "start"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Tipo de arquivo não permitido", response.data.get("error", ""))

    def test_create_document_missing_document_type(self):
        file = SimpleUploadedFile("new_doc.pdf", b"dummy_content", content_type="application/pdf")
        data = {"file": file}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Tipo de documento é obrigatório", response.data.get("error", ""))


    def test_delete_document(self):
        url = reverse('document-detail', args=[self.document.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.filter(deleted_at=None).count(), 0)
