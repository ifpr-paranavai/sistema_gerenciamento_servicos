from rest_framework import serializers
from appointment.models import Appointment, Review
from authentication.api.serializers import SimpleUserSerializer
from documents.api.document_serializers import DocumentSerializer
from documents.models.document import Document
from service.api.serializers import ServiceSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    document_file = serializers.FileField(write_only=True, required=False)
    client = SimpleUserSerializer(read_only=True)
    provider = SimpleUserSerializer(read_only=True)
    services = ServiceSerializer(many=True)
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
            'is_completed', 
            'documents', 
            'document_file', 
            'rating',
            'observation'
        ]

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        appointment = Appointment.objects.create(**validated_data)
        appointment.services.set(services)
        return appointment
    
    def get_rating(self, obj):
        review = obj.reviews.first()
        if review:
            return review.rating
        return None


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
