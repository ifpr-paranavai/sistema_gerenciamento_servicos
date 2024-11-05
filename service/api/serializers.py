from django.db import transaction
from rest_framework import serializers
from documents.api.document_template_serializers import ServiceDocumentRequirementSerializer
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement
from service.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    document_requirements = ServiceDocumentRequirementSerializer(many=True, required=False)
    rating_avg = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'cost', 'duration', 'document_requirements', 'rating_avg']

    def get_rating_avg(self, obj):
        ratings = []
        for appointment in obj.appointments.all():
            ratings.extend([review.rating for review in appointment.reviews.all()])
        return sum(ratings) / len(ratings) if ratings else None

    def validate_document_requirements(self, document_requirements_data):
        """
        Valida se os templates de documentos existem antes de criar/atualizar o serviço
        """
        if document_requirements_data:
            template_ids = [doc['document_template'].id for doc in document_requirements_data]
            existing_templates = DocumentTemplate.objects.filter(id__in=template_ids).count()
            
            if existing_templates != len(template_ids):
                raise serializers.ValidationError({
                    'document_requirements': 'Um ou mais templates de documentos não existem.'
                })
        return document_requirements_data
    
    def create(self, validated_data):
        document_requirements_data = validated_data.pop('document_requirements', [])
        
        try:
            with transaction.atomic():
                service = super().create(validated_data)
                
                for doc_req in document_requirements_data:
                    template_id = doc_req.get('document_template').id
                    if template_id:
                        ServiceDocumentRequirement.objects.create(
                            service=service,
                            document_template_id=template_id,
                            is_required=doc_req.get('is_required', False)
                        )
                return service
        except Exception as e:
            raise serializers.ValidationError(f'Erro ao criar requisitos de documentos: {str(e)}')

    def update(self, instance, validated_data):
        document_requirements_data = validated_data.pop('document_requirements', [])
        
        try:
            with transaction.atomic():
                service = super().update(instance, validated_data)
                
                service.document_requirements.all().delete()
                
                for doc_req in document_requirements_data:
                    template_id = doc_req.get('document_template').id
                    if template_id:
                        ServiceDocumentRequirement.objects.create(
                            service=service,
                            document_template_id=template_id,
                            is_required=doc_req.get('is_required', False)
                        )
                return service
        except Exception as e:
            raise serializers.ValidationError(f'Erro ao criar requisitos de documentos: {str(e)}')