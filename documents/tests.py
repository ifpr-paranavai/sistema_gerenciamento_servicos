from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models.document import Document
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement
from service.models import Service

class DocumentModelTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            cost=10.00,
            duration=60
        )
        self.document = Document.objects.create(
            service=self.service,
            file=SimpleUploadedFile("test.pdf", b"file_content"),
            document_type='start'
        )

    def test_document_creation(self):
        self.assertTrue(isinstance(self.document, Document))
        self.assertEqual(self.document.__str__(), f"Document for Service {self.service.id}")

    def test_file_extension(self):
        self.assertEqual(self.document.file_extension, '.pdf')

    def test_filename(self):
      self.assertTrue(self.document.filename.startswith('test'))
      self.assertTrue(self.document.filename.endswith('.pdf'))

class ServiceDocumentRequirementTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            cost=10.00,
            duration=60
        )
        self.doc_template1 = DocumentTemplate.objects.create(
            name="RG", 
            description="RG Document", 
            file_types="pdf,jpg,png"
        )
        self.doc_template2 = DocumentTemplate.objects.create(
            name="CPF", 
            description="CPF Document", 
            file_types="pdf,jpg,png"
        )
        
        ServiceDocumentRequirement.objects.create(
            service=self.service, 
            document_template=self.doc_template1, 
            is_required=True
        )
        ServiceDocumentRequirement.objects.create(
            service=self.service, 
            document_template=self.doc_template2, 
            is_required=True
        )

    def test_check_required_documents(self):
        result = self.service.check_required_documents()
        self.assertFalse(result['is_complete'])
        self.assertEqual(set(result['missing_documents']), {'RG', 'CPF'})

        Document.objects.create(
            service=self.service, 
            file=SimpleUploadedFile("rg.pdf", b"file_content"),
            document_type='RG'
        )
        result = self.service.check_required_documents()
        self.assertFalse(result['is_complete'])
        self.assertEqual(result['missing_documents'], ['CPF'])

        Document.objects.create(
            service=self.service, 
            file=SimpleUploadedFile("cpf.pdf", b"file_content"),
            document_type='CPF'
        )
        result = self.service.check_required_documents()
        self.assertTrue(result['is_complete'])
        self.assertEqual(result['missing_documents'], [])