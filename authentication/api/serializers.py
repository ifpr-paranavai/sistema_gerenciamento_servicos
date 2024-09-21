from rest_framework import serializers
from authentication.models import User
from core.api.serializers import FeatureSerializer
from core.models.role import Role
        
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='id'
    )
    features = FeatureSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'cpf', 'role', 'features']
        extra_kwargs = {
            'senha': {'write_only': True},
        }

    def create(self, validated_data):
        roles_data = validated_data.pop('role')
        user = User.objects.create(**validated_data)
        user.role = roles_data
        user.features.set(roles_data.features.all())
        return user
