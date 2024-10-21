from rest_framework import serializers
from service.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    ratting_avg = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = '__all__'

    def get_ratting_avg(self, obj):
        rattings = []
        for appointment in obj.appointments.all():
            rattings = rattings + [review.rating for review in appointment.reviews.all()]

        if rattings:
            return sum(rattings) / len(rattings)
        return None
            