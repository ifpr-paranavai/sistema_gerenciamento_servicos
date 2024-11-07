from rest_framework import serializers
from appointment.models import Appointment, Review
from authentication.api.serializers import SimpleUserSerializer
from documents.api.document_serializers import DocumentSerializer
from documents.models.document import Document
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement
from service.api.serializers import ServiceSerializer
from service.models.service import Service

class AppointmentSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    document_file = serializers.FileField(write_only=True, required=False)
    client = SimpleUserSerializer(read_only=True)
    provider = SimpleUserSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        source='services',
        write_only=True,
        many=True,
        queryset=Service.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 
            'appointment_date', 
            'status', 
            'client', 
            'provider', 
            'services',
            'service_ids', 
            'is_completed', 
            'documents', 
            'document_file', 
            'rating',
            'observation'
        ]

    def validate(self, attrs):
        """
        Valida se todos os documentos obrigatórios foram enviados
        """
        request = self.context.get('request')
        
        if not request:
            raise serializers.ValidationError("Contexto da requisição não encontrado")
 
        services = request.data.get('services', []).split(',')
        
        required_documents = ServiceDocumentRequirement.objects.filter(
            service__in=services,
            is_required=True
        ).select_related('document_template')

        for requirement in required_documents:
            document_key = f'document_{requirement.id}'
            if document_key not in request.FILES:
                raise serializers.ValidationError({
                    'documents': f'Documento obrigatório faltando: {requirement.document_template.name}'
                })

        return attrs
    
    def create(self, validated_data):
        request = self.context.get('request')
        client_id = request.data.get('client')
        provider_id = request.data.get('provider')
        
        if not client_id or not provider_id:
            raise serializers.ValidationError({
                "error": "Client e Provider são obrigatórios"
            })

        services = validated_data.pop('services', [])
        
        try:
            appointment = Appointment.objects.create(
                client_id=client_id,
                provider_id=provider_id,
                **validated_data
            )
            
            appointment.services.set(services)

            self._save_documents(request.FILES, appointment, services)

            return appointment

        except Exception as e:
            if 'appointment' in locals():
                appointment.delete()
            raise serializers.ValidationError(str(e))
    
    def _save_documents(self, files, appointment, services):
        """
        Salva os documentos associados ao agendamento
        """
        document_requirements = DocumentTemplate.objects.filter(
            service__in=services
        ).select_related('document_template')

        for requirement in document_requirements:
            document_key = f'document_{requirement.id}'
            
            if document_key in files:
                file = files[document_key]
                
                # Valida o tipo do arquivo
                file_extension = file.name.split('.')[-1].lower()
                allowed_types = requirement.document_template.file_types
                
                if isinstance(allowed_types, str):
                    allowed_types = eval(allowed_types)
                
                if file_extension not in allowed_types:
                    raise serializers.ValidationError(
                        f'Tipo de arquivo inválido para {requirement.document_template.name}. '
                        f'Tipos permitidos: {", ".join(allowed_types)}'
                    )

                document = Document.objects.create(
                    name=file.name,
                    file=file,
                    document_template=requirement.document_template,
                    appointment=appointment
                )
                
                self.document_file.set(document)
                
    
    def get_rating(self, obj):
        review = obj.reviews.first()
        if review:
            return review.rating
        return None


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
