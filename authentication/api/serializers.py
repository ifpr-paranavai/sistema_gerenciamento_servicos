from django.utils import timezone
from rest_framework import serializers
from appointment.models.appointment import Appointment
from authentication.models import User
from core.api.serializers import FeatureSerializer
from core.models.role import Role
from core.api.serializers import ProfileSerializer
        
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='id'
    )
    features = FeatureSerializer(many=True, read_only=True)
    profile = ProfileSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'cpf', 'role', 'features', 'profile']
        extra_kwargs = {
            'senha': {'write_only': True},
        }
       
    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if self.context.get('remove_password'):
            self.fields.pop('password')
        if self.context.get('remove_features'):
            self.fields.pop('features')
        
    def create(self, validated_data):
        roles_data = validated_data.pop('role')
        user = User.objects.create(**validated_data)
        user.role = roles_data
        user.features.set(roles_data.features.all())
        return user

class SimpleUserSerializer(serializers.ModelSerializer):
    cpf = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'cpf']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def get_cpf(self, obj):
        return f'{obj.cpf[:3]}.***.***-{obj.cpf[9:]}'
    

class ProviderScheduleSerializer(SimpleUserSerializer):
    appointments = serializers.SerializerMethodField()

    class Meta(SimpleUserSerializer.Meta):
        fields = SimpleUserSerializer.Meta.fields + ['appointments']

    def get_appointments(self, obj):
        appointments = Appointment.objects.filter(
            provider=obj,
            deleted_at__isnull=True,
            status__in=[Appointment.Status.PENDING, Appointment.Status.IN_PROGRESS],
            appointment_date__gte=timezone.now()  # Apenas futuros
        ).order_by('appointment_date')

        return [{
            'id': app.id,
            'start': app.appointment_date,
            'end': app.appointment_date + timezone.timedelta(minutes=app.services.first().duration if app.services.exists() else 0),
            'service': app.services.first().name if app.services.exists() else None,
        } for app in appointments]