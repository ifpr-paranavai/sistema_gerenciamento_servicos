# serializers.py
from rest_framework import serializers
from appointment.models.appointment import Appointment

class ServiceStatSerializer(serializers.Serializer):
    serviceName = serializers.CharField()
    date = serializers.DateTimeField()
    totalValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    averageValue = serializers.DecimalField(max_digits=10, decimal_places=2)

class AppointmentSerializer(serializers.ModelSerializer):
    serviceName = serializers.SerializerMethodField()
    clientName = serializers.SerializerMethodField()
    providerName = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'serviceName', 'clientName', 'providerName', 'appointment_date', 'status')

    def get_serviceName(self, obj):
        return ", ".join([service.name for service in obj.services.all()])

    def get_clientName(self, obj):
        return obj.client.name if obj.client else None

    def get_providerName(self, obj):
        return obj.provider.name if obj.provider else None

class DashboardStatSerializer(serializers.Serializer):
    totalRevenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    serviceStats = ServiceStatSerializer(many=True)
    currentAppointments = AppointmentSerializer(many=True)
    upcomingAppointments = AppointmentSerializer(many=True)