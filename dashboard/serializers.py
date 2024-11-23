from rest_framework import serializers

class ServiceStatSerializer(serializers.Serializer):
    serviceId = serializers.IntegerField(source='id')
    serviceName = serializers.CharField(source='name')
    totalValue = serializers.IntegerField()  # Alterado para inteiro pois representa contagem

class ServiceDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class AppointmentStatSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    serviceName = serializers.SerializerMethodField()
    clientName = serializers.CharField(source='client.name')
    date = serializers.DateTimeField(source='appointment_date')
    status = serializers.CharField()
    services = ServiceDetailSerializer(many=True)  # Adicionado campo services

    def get_serviceName(self, obj):
        return ', '.join(s.name for s in obj.services.all())

class DashboardStatSerializer(serializers.Serializer):
    totalRevenue = serializers.IntegerField()  # Alterado para inteiro pois representa contagem
    serviceStats = ServiceStatSerializer(many=True)
    currentAppointments = AppointmentStatSerializer(many=True)
    upcomingAppointments = AppointmentStatSerializer(many=True)