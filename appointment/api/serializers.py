from django.utils import timezone
from rest_framework import serializers
from appointment.models import Appointment, Review
from authentication.api.serializers import SimpleUserSerializer
from documents.api.document_serializers import DocumentSerializer
from documents.models.document import Document
from documents.models.document_template import ServiceDocumentRequirement
from service.api.serializers import ServiceSerializer
from service.models.service import Service

class AppointmentSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
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
    
    def get_rating(self, obj):
        review = obj.reviews.first()
        if review:
            return review.rating
        return None
    
    def get_documents(self, obj):
        active_documents = obj.documents.filter(deleted_at__isnull=True)
        return DocumentSerializer(active_documents, many=True).data

    def validate(self, attrs):
        request = self.context.get('request')
        
        if not request:
            raise serializers.ValidationError("Contexto da requisição não encontrado")
 
        service_id = request.data.get('services')
        provider_id = request.data.get('provider')
        appointment_date = request.data.get('appointment_date')

        if not all([service_id, provider_id, appointment_date]):
            raise serializers.ValidationError({
                "error": "Serviço, prestador e data são obrigatórios"
            })

        try:
            service = Service.objects.get(id=service_id)
            exclude_id = self.instance.id if self.instance else None
            
            availability = Appointment.check_availability(
                appointment_date,
                provider_id,
                service.duration,
                exclude_id
            )

            if not availability['is_available']:
                conflicts = availability['conflicts']
                conflict_messages = [
                    f"Conflito com agendamento de {c['service']} para {c['client']} "
                    f"({c['start'].strftime('%d/%m/%Y %H:%M')} - "
                    f"{c['end'].strftime('%d/%m/%Y %H:%M')}) "
                    f"[Status: {c['status']}]"
                    for c in conflicts
                ]
                
                raise serializers.ValidationError({
                    'appointment_date': [
                        "Horário indisponível para agendamento.",
                        *conflict_messages
                    ]
                })

            services = [service_id]
            required_documents = ServiceDocumentRequirement.objects.filter(
                service__in=services,
                is_required=True
            ).select_related('document_template')

            for requirement in required_documents:
                if f'document_requirement_{requirement.id}' not in request.FILES:
                    raise serializers.ValidationError({
                        'documents': f'Documento obrigatório faltando: {requirement.document_template.name}'
                    })

            return attrs

        except Service.DoesNotExist:
            raise serializers.ValidationError({"service": "Serviço não encontrado"})
    
    def create(self, validated_data):
        request = self.context.get('request')
        client_id = request.data.get('client')
        provider_id = request.data.get('provider')
        service_id = request.data.get('services')
        
        if not client_id or not provider_id:
            raise serializers.ValidationError({
                "error": "Client e Provider são obrigatórios"
            })

        if not service_id:
            raise serializers.ValidationError({
                "error": "Serviço é obrigatório"
            })

        try:
            validated_data.pop('services', None)
            
            appointment = Appointment.objects.create(
                client_id=client_id,
                provider_id=provider_id,
                **validated_data
            )
            
            service = Service.objects.get(id=service_id)
            appointment.services.add(service)

            documents = self._save_documents(request.FILES, appointment, [service_id])
            
            if documents:
                appointment.documents.add(*documents)

            return appointment

        except Exception as e:
            if 'appointment' in locals():
                appointment.delete()
            raise serializers.ValidationError(str(e))
    
    def _save_documents(self, files, appointment, services):
        """
        Salva os documentos associados ao agendamento
        """
        documents_created = []
        document_requirements = ServiceDocumentRequirement.objects.filter(
            service__in=services
        ).select_related('document_template')

        for requirement in document_requirements:
            file_key = f'document_requirement_{requirement.id}'
            
            if file_key in files:
                file = files[file_key]
                
                file_extension = file.name.split('.')[-1].lower()
                allowed_types = requirement.document_template.file_types
                
                if isinstance(allowed_types, str):
                    allowed_types = eval(allowed_types)
                
                if file_extension not in allowed_types:
                    raise serializers.ValidationError(
                        f'Tipo de arquivo inválido para {requirement.document_template.name}. '
                        f'Tipos permitidos: {", ".join(allowed_types)}'
                    )

                try: 
                    document = Document(
                        file_name=file.name,
                        file_type=file.content_type.split('/')[1],
                        file_size=file.size,
                        document_type='start'
                    )
                    
                    document.file_content = file.read()
                    document.save()
                    
                    documents_created.append(document)
                except Exception as e:
                    
                    for doc in documents_created:
                        doc.delete()
                    raise serializers.ValidationError(f"Erro ao salvar documento: {str(e)}")

        return documents_created
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Contexto da requisição não encontrado")

        service_id = request.data.get('services')
        client_id = request.data.get('client')
        provider_id = request.data.get('provider')
        status = request.data.get('status')
        appointment_date = request.data.get('appointment_date')
        observation = request.data.get('observation')

        try:
            if status:
                instance.status = status
            if appointment_date:
                instance.appointment_date = appointment_date
            if observation is not None:
                instance.observation = observation
            if client_id:
                instance.client_id = client_id
            if provider_id:
                instance.provider_id = provider_id
            if service_id:
                service = Service.objects.get(id=service_id)
                instance.services.clear()
                instance.services.add(service)

            instance.save()
            
            new_documents = self._process_documents_update(request.FILES, instance, service_id)

            if new_documents:
                instance.documents.add(*new_documents)

            return instance

        except Exception as e:
            raise serializers.ValidationError(str(e))
    
    def _process_documents_update(self, files, appointment, service_id):
        """
        Processa os documentos na atualização usando soft delete
        """
        if not files:
            return []
        
        documents_created = []
        
        try:
            appointment.documents.update(deleted_at=timezone.now())
            document_requirements = ServiceDocumentRequirement.objects.filter(
                service=service_id
            ).select_related('document_template')
            
            for requirement in document_requirements:
                file_key = f'document_requirement_{requirement.id}'
                
                if file_key in files:
                    file = files[file_key]
                    
                    file_extension = file.name.split('.')[-1].lower()
                    allowed_types = requirement.document_template.file_types
                    
                    if isinstance(allowed_types, str):
                        allowed_types = eval(allowed_types)
                    
                    if file_extension not in allowed_types:
                        raise serializers.ValidationError(
                            f'Tipo de arquivo inválido para {requirement.document_template.name}. '
                            f'Tipos permitidos: {", ".join(allowed_types)}'
                        )

                    if appointment.documents.filter(file_name=file.name).exists():
                        document = appointment.documents.get(file_name=file.name)
                        document.deleted_at = None
                        document.save()
                        documents_created.append(document)
                    else:
                        document = Document(
                            file_name=file.name,
                            file_type=file.content_type.split('/')[1],
                            file_size=file.size,
                            document_type='start'
                        )
                        
                        document.file_content = file.read()
                        document.save()
                        
                        documents_created.append(document)
                
            return documents_created
        except Exception as e:
            for doc in documents_created:
                doc.delete()
            raise serializers.ValidationError(f"Erro ao atualizar documentos: {str(e)}")

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
