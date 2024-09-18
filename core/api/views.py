from core.models import Profile, Feature, Role
from core.api.serializers import ProfileSerializer, FeatureSerializer, RoleSerializer
from core.models.mixins import DynamicPermissionModelViewSet

class ProfileViewSet(DynamicPermissionModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class FeatureViewSet(DynamicPermissionModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class RoleViewSet(DynamicPermissionModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
