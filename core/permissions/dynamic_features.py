from typing import Set, Dict, List
from django.apps import apps as django_apps
from django.db import IntegrityError
from .enums import DjangoActions

class ModelFeatureGenerator:
    EXCLUDED_APPS = {'admin', 'contenttypes', 'sessions', 'auth'}
    
    def __init__(self):
        self.features: Set[str] = set()
        self.descriptions: Dict[str, str] = {}
        
    def generate_model_feature(self, app_label: str, model_name: str, action: DjangoActions) -> str:
        """Gera o nome da feature para um modelo e ação específicos"""
        return f"{app_label}.{action.value}_{model_name}"
        
    def scan_models(self) -> None:
        """Escaneia todos os modelos do Django e gera as features correspondentes"""
        for model in django_apps.get_models():
            if model._meta.app_label in self.EXCLUDED_APPS:
                continue

            app_label = model._meta.app_label
            model_name = model._meta.model_name
            
            for action in DjangoActions:
                feature_name = self.generate_model_feature(app_label, model_name, action)
                self.features.add(feature_name)
                self.descriptions[feature_name] = f"Can {action.value} {model_name} in {app_label}"

    def get_model_features(self, app_label: str, model_name: str) -> List[str]:
        """Retorna todas as features para um modelo específico"""
        return [
            self.generate_model_feature(app_label, model_name, action)
            for action in DjangoActions
        ]

class DynamicFeatures:
    """Classe para gerenciar features dinâmicas do sistema"""
    
    def __init__(self):
        self._generator = ModelFeatureGenerator()
        self._generator.scan_models()
        
    @property
    def features(self) -> Set[str]:
        return self._generator.features
    
    @property
    def descriptions(self) -> Dict[str, str]:
        return self._generator.descriptions
    
    def get_model_features(self, app_label: str, model_name: str) -> List[str]:
        return self._generator.get_model_features(app_label, model_name)
    
    def create_all_features(self) -> None:
        """Cria todas as features dinâmicas no banco de dados"""
        Feature = django_apps.get_model('core', 'Feature')
        
        for feature_name in self.features:
            try:
                Feature.objects.get_or_create(
                    name=feature_name,
                    defaults={'description': self.descriptions[feature_name]}
                )
            except IntegrityError:
                feature = Feature.objects.get(name=feature_name)
                feature.description = self.descriptions[feature_name]
                feature.save()