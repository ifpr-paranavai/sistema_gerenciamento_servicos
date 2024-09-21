from django.db import models
from core.models.mixins import TimeStampedModel

class Service(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()

    def check_required_documents(self):
        required_documents = self.document_requirements.filter(is_required=True)
        provided_documents = self.documents.all()
        
        missing_documents = []
        for req in required_documents:
            if not provided_documents.filter(document_type=req.document_template.name).exists():
                missing_documents.append(req.document_template.name)
        
        return {
            'is_complete': len(missing_documents) == 0,
            'missing_documents': missing_documents
        }