from django.utils import timezone
from rest_framework import serializers
from typing import List, Dict, Any
from appointment.models import Appointment
from appointment.models.review import Review
from authentication.api.serializers import SimpleUserSerializer
from documents.api.document_serializers import DocumentSerializer
from documents.models.document import Document
from documents.models.document_template import ServiceDocumentRequirement
from service.api.serializers import ServiceSerializer
from service.models.document_service import DocumentService
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
    review = serializers.SerializerMethodField()
    extra_documents = serializers.SerializerMethodField()
    extra_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_date', 'status', 'client', 'provider', 
            'services', 'service_ids', 'is_completed', 'documents', 
            'document_file', 'rating', 'observation', 'review', 
            'extra_documents', 'extra_files', 
        ]
        read_only_fields = ['is_completed', 'rating']

    def get_rating(self, obj: Appointment) -> int:
        review = obj.reviews.first()
        return review.rating if review else None
    
    def get_documents(self, obj: Appointment) -> List[Dict]:
        """Retorna apenas documentos ativos (não deletados)"""
        active_documents = obj.documents.filter(deleted_at__isnull=True)
        return DocumentSerializer(active_documents, many=True).data
    
    def get_extra_documents(self, obj: Appointment) -> List[Dict]:
        """Retorna apenas documentos extras ativos"""
        active_documents = obj.extra_documents.filter(deleted_at__isnull=True)
        return DocumentSerializer(active_documents, many=True).data

    def _process_extra_documents(
        self,
        files: List[Any],
        is_update: bool = False,
        appointment: Appointment = None
    ) -> List[Document]:
        """Processa documentos extras do agendamento"""
        if not files:
            return []

        documents_created = []
        max_file_size = 5 * 1024 * 1024  # 5MB

        try:
            if is_update and appointment:
                appointment.extra_documents.update(deleted_at=timezone.now())

            for file in files:
                if file.size > max_file_size:
                    raise serializers.ValidationError(
                        f"Arquivo {file.name} excede o tamanho máximo permitido (5MB)"
                    )

                if is_update and appointment and appointment.extra_documents.filter(
                    file_name=file.name
                ).exists():
                    document = appointment.extra_documents.get(file_name=file.name)
                    document.deleted_at = None
                    document.save()
                else:
                    document = Document.objects.create(
                        file_name=file.name,
                        file_content=file.read(),
                        file_type=file.name.split('.')[-1].lower(),
                        document_type='extra'
                    )
                documents_created.append(document)

            return documents_created

        except Exception as e:
            for doc in documents_created:
                doc.delete()
            raise serializers.ValidationError(f"Erro ao processar documentos extras: {str(e)}")

    def validate(self, attrs: Dict) -> Dict:
        """Validação completa dos dados do agendamento"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Contexto da requisição não encontrado")

        self._validate_required_fields(request.data)
        self._validate_service_availability(request.data, attrs)
        self._validate_required_documents(request.data, request.FILES)

        return attrs

    def _validate_required_fields(self, data: Dict) -> None:
        """Valida campos obrigatórios"""
        required_fields = {
            'services': 'Serviço é obrigatório',
            'provider': 'Prestador é obrigatório',
            'appointment_date': 'Data do agendamento é obrigatória'
        }

        missing_fields = {
            field: message for field, message in required_fields.items()
            if not data.get(field)
        }

        if missing_fields:
            raise serializers.ValidationError(missing_fields)

    def _validate_service_availability(self, request_data: Dict, attrs: Dict) -> None:
        """Valida disponibilidade do serviço"""
        try:
            service_id = request_data.get('services')
            service = Service.objects.get(id=service_id)
            exclude_id = self.instance.id if self.instance else None
            
            availability = Appointment.check_availability(
                request_data.get('appointment_date'),
                request_data.get('provider'),
                service.duration,
                exclude_id
            )

            if not availability['is_available']:
                self._raise_conflict_error(availability['conflicts'])
        except Service.DoesNotExist:
            raise serializers.ValidationError({"service": "Serviço não encontrado"})

    def _raise_conflict_error(self, conflicts: List[Dict]) -> None:
        """Formata e lança erro de conflito de horário"""
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

    def _validate_required_documents(self, data: Dict, files: Dict) -> None:
        """Valida documentos obrigatórios"""
        service_id = data.get('services')
        if not service_id:
            return

        required_docs = ServiceDocumentRequirement.objects.filter(
            service__in=[service_id],
            is_required=True
        ).select_related('document_template')

        for requirement in required_docs:
            if f'document_requirement_{requirement.id}' not in files:
                raise serializers.ValidationError({
                    'documents': f'Documento obrigatório faltando: {requirement.document_template.name}'
                })

    def create(self, validated_data: Dict[str, Any]) -> Appointment:
        request = self.context.get('request')
        client_id = request.data.get('client')
        provider_id = request.data.get('provider')
        service_id = request.data.get('services')
        extra_files = []
        for key in request.FILES.keys():
            if key.startswith('extra_document_'):
                extra_files.append(request.FILES[key])


        try:
            # Remove services do validated_data pois será adicionado depois
            validated_data.pop('services', None)
            validated_data.pop('extra_files', None)
            
            appointment = Appointment.objects.create(
                client_id=client_id,
                provider_id=provider_id,
                **validated_data
            )
            
            # Adiciona serviço
            service = Service.objects.get(id=service_id)
            appointment.services.add(service)

            # Processa documentos
            documents = self._process_documents(
                request.FILES, 
                [service_id], 
                is_update=False
            )
            
            if documents:
                appointment.documents.add(*documents)

            if extra_files:
                extra_documents = self._process_extra_documents(extra_files)
                if extra_documents:
                    appointment.extra_documents.add(*extra_documents)

            return appointment

        except Exception as e:
            if 'appointment' in locals():
                appointment.delete()
            raise serializers.ValidationError(str(e))

    def update(self, instance: Appointment, validated_data: Dict[str, Any]) -> Appointment:
        """Atualiza agendamento existente"""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Contexto da requisição não encontrado")

        try:
            extra_files = []
            for key in request.FILES.keys():
                if key.startswith('extra_document_'):
                    extra_files.append(request.FILES[key])
            validated_data.pop('extra_files', None)

            instance = self._update_basic_fields(instance, request.data)
            
            service_id = request.data.get('services')
            if service_id:
                service = Service.objects.get(id=service_id)
                instance.services.clear()
                instance.services.add(service)

            if request.FILES:
                new_documents = self._process_documents(
                    request.FILES,
                    [service_id] if service_id else [s.id for s in instance.services.all()],
                    is_update=True,
                    appointment=instance
                )
                if new_documents:
                    instance.documents.add(*new_documents)
                
                if extra_files:
                    new_extra_documents = self._process_extra_documents(
                        extra_files,
                        is_update=True,
                        appointment=instance
                    )
                    if new_extra_documents:
                        instance.extra_documents.add(*new_extra_documents)

            instance.save()
            return instance

        except Exception as e:
            raise serializers.ValidationError(str(e))

    def _update_basic_fields(self, instance: Appointment, data: Dict) -> Appointment:
        """Atualiza campos básicos do agendamento"""
        fields = {
            'status': 'status',
            'appointment_date': 'appointment_date',
            'observation': 'observation',
            'client_id': 'client_id',
            'provider_id': 'provider_id'
        }

        for field, attr in fields.items():
            if field in data and data[field] is not None:
                setattr(instance, attr, data[field])

        return instance

    def _process_documents(
        self, 
        files: Dict, 
        service_ids: List[int], 
        is_update: bool = False,
        appointment: Appointment = None
    ) -> List[Document]:
        """Processa documentos do agendamento"""
        if not files:
            return []

        document_service = DocumentService()
        documents_created = []

        try:
            if is_update and appointment:
                appointment.documents.update(deleted_at=timezone.now())

            requirements = ServiceDocumentRequirement.objects.filter(
                service__in=service_ids
            ).select_related('document_template')

            for requirement in requirements:
                file_key = f'document_requirement_{requirement.id}'
                if file_key in files:
                    file = files[file_key]
                    
                    # Valida tipo do arquivo
                    document_service.validate_file_type(
                        file, 
                        requirement.document_template.file_types
                    )

                    # Verifica se documento já existe (em caso de update)
                    if is_update and appointment and appointment.documents.filter(
                        file_name=file.name
                    ).exists():
                        document = appointment.documents.get(file_name=file.name)
                        document.deleted_at = None
                        document.save()
                        documents_created.append(document)
                    else:
                        # Cria novo documento
                        document = Document.objects.create(
                            file_name=file.name,
                            file_content=file.read(),
                            file_type=file.name.split('.')[-1].lower(),
                            document_type='start'
                        )
                        documents_created.append(document)

            return documents_created

        except Exception as e:
            for doc in documents_created:
                doc.delete()
            raise serializers.ValidationError(f"Erro ao processar documentos: {str(e)}")
        
    def get_review(self, obj: Appointment) -> Dict:
        # tem que trazer o review do user logado
        user = self.context.get('request').user
        review = obj.reviews.filter(user=user).first()
        return ReviewSerializer(review).data if review else None
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
