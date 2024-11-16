from django.apps import apps as django_apps
from django.db import transaction
from typing import Dict, Any, List
from ..permissions.dynamic_features import DynamicFeatures
from ..permissions.descriptions import FEATURE_DESCRIPTIONS
from ..permissions.enums import (
    MenuFeatures, HomeFeatures, ProfileFeatures, TechnicalFeatures
)

def create_dynamic_features():
    """Cria todas as features do sistema de forma otimizada"""
    Feature = django_apps.get_model('core', 'Feature')
    
    features_to_create: Dict[str, Dict[str, Any]] = {}
    
    dynamic_features = DynamicFeatures()
    for feature_name, description in dynamic_features.descriptions.items():
        features_to_create[feature_name] = {
            'name': feature_name,
            'description': description
        }
    
    enum_features = {
        f.value: FEATURE_DESCRIPTIONS.get(f, f"Permission for {f.value}") 
        for enum_class in [MenuFeatures, HomeFeatures, ProfileFeatures, TechnicalFeatures]
        for f in enum_class
    }
    
    for name, description in enum_features.items():
        features_to_create[name] = {
            'name': name,
            'description': description
        }
    
    with transaction.atomic():

        existing_features = {
            f.name: f for f in Feature.objects.all()
        }
        
        features_to_update: List[Any] = []
        features_to_create_list: List[Dict[str, Any]] = []
        
        for name, data in features_to_create.items():
            if name in existing_features:
                feature = existing_features[name]
                if feature.description != data['description']:
                    feature.description = data['description']
                    features_to_update.append(feature)
            else:
                features_to_create_list.append(data)
        

        if features_to_update:
            Feature.objects.bulk_update(
                features_to_update,
                ['description']
            )
        

        if features_to_create_list:
            Feature.objects.bulk_create([
                Feature(**data)
                for data in features_to_create_list
            ])