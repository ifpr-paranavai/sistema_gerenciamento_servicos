from django.apps import apps as django_apps
from .permissions.dynamic_features import DynamicFeatures
from .permissions.descriptions import FEATURE_DESCRIPTIONS
from .permissions.enums import (
    MenuFeatures, HomeFeatures, ProfileFeatures, TechnicalFeatures
)

def create_dynamic_features():
    """Cria todas as features do sistema"""
    Feature = django_apps.get_model('core', 'Feature')
    
    # Criar features dinâmicas
    dynamic_features = DynamicFeatures()
    dynamic_features.create_all_features()
    
    # Criar features definidas nas enums
    all_features = {
        **{f.value: FEATURE_DESCRIPTIONS.get(f, f"Permission for {f.value}") 
           for enum_class in [MenuFeatures, HomeFeatures, ProfileFeatures, TechnicalFeatures]
           for f in enum_class}
    }

    for name, description in all_features.items():
        Feature.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )