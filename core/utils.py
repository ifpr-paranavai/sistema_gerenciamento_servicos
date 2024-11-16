# core/utils.py
from django.apps import apps as django_apps
from django.db import transaction
from .permissions.dynamic_features import DynamicFeatures
from typing import Dict, Set

def create_dynamic_features():
    """
    Cria todas as features do sistema de forma otimizada em uma única transação.
    Inclui features dinâmicas, fixas e baseadas em enums.
    Remove features obsoletas.
    """
    Feature = django_apps.get_model('core', 'Feature')
    
    with transaction.atomic():
        feature_manager = DynamicFeatures()
        
        # Obter todas as features definidas
        all_features: Dict[str, str] = feature_manager.descriptions
        valid_feature_names: Set[str] = set(all_features.keys())
        
        # Obter features existentes
        existing_features = {
            f.name: f for f in Feature.objects.all()
        }
        
        features_to_create = []
        features_to_update = []
        
        # Criar ou atualizar features
        for name, description in all_features.items():
            if name in existing_features:
                feature = existing_features[name]
                if feature.description != description:
                    feature.description = description
                    features_to_update.append(feature)
            else:
                features_to_create.append(
                    Feature(name=name, description=description)
                )
        
        # Criar novas features em massa
        if features_to_create:
            Feature.objects.bulk_create(features_to_create)
        
        # Atualizar features existentes em massa
        if features_to_update:
            Feature.objects.bulk_update(features_to_update, ['description'])
            
        # Remover features que não estão mais definidas
        obsolete_features = set(existing_features.keys()) - valid_feature_names
        if obsolete_features:
            Feature.objects.filter(name__in=obsolete_features).delete()