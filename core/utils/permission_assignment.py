from django.apps import apps as django_apps
from ..permissions.role_permissions import ROLE_PERMISSIONS

def assign_role_permissions():
    """Atribui permissões aos usuários baseado em seus roles"""
    User = django_apps.get_model('authentication', 'User')
    Feature = django_apps.get_model('core', 'Feature')
    
    features = {feature.name: feature for feature in Feature.objects.all()}
    
    for user in User.objects.select_related('role').all():
        if not user.role:
            continue
            
        role_type = user.role.role_type
        if role_type in ROLE_PERMISSIONS:
            user.features.clear()
            
            permission_group = ROLE_PERMISSIONS[role_type]
            feature_objects = [
                features[feat.value] 
                for feat in permission_group.features 
                if feat.value in features
            ]
            user.features.add(*feature_objects)