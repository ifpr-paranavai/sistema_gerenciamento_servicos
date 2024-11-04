import base64
import os
from django.db import models
from django.core.validators import FileExtensionValidator
from core.models.mixins import TimeStampedModel

def document_upload_path(instance, filename):
    return f'documents/{filename}'

class Document(TimeStampedModel):
    DOCUMENT_TYPES = (
        ('start', 'Start of Service'),
        ('end', 'End of Service'),
    )
    
    file_name = models.CharField(max_length=255, blank=True)
    file_content = models.BinaryField(blank=True)
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.IntegerField(blank=True, null=True)
    document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    
    def __str__(self):
        return f"{self.file_name} - {self.document_type}"

    @property
    def file_extension(self):
        return self.file_name.split('.')[-1] if self.file_name else ''

    class Meta:
        ordering = ['-updated_at']