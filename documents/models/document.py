import os
from django.db import models
from django.core.validators import FileExtensionValidator
from core.models.mixins import TimeStampedModel
from service.models import Service

def document_upload_path(instance, filename):
    return f'documents/service_{instance.service.id}/{filename}'

class Document(TimeStampedModel):
    DOCUMENT_TYPES = (
        ('start', 'Start of Service'),
        ('end', 'End of Service'),
    )
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    
    def __str__(self):
        return f"{self.file.name} - {self.document_type}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1]

    class Meta:
      ordering = ['-updated_at'] 