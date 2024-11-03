from django.db import models
from core.models.mixins import TimeStampedModel
from documents.models.document import Document
from service.models import Service

class DocumentTemplate(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    file_types = models.CharField(max_length=255, help_text="Comma-separated list of allowed file extensions", default='pdf,jpg,jpeg')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='document_templates', blank=True, null=True)
    
    def __str__(self):
        return self.name

class ServiceDocumentRequirement(TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='document_requirements')
    document_template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, null=True, blank=True)
    is_required = models.BooleanField(default=False)

    class Meta:
        unique_together = ['service', 'document_template']

    def __str__(self):
        return f"{self.service.name} - {self.document_template.name}"