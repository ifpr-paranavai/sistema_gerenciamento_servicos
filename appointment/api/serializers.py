from rest_framework import serializers
from appointment.models import Appointment, Review
from documents.api.document_serializers import DocumentSerializer
from documents.models.document import Document

class AppointmentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(many=True, read_only=True)
    document_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = ['id', 'appointment_date', 'status', 'client', 'provider', 'services', 'is_completed', 'document', 'document_file']

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        appointment = Appointment.objects.create(**validated_data)
        appointment.services.set(services)
        return appointment

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
