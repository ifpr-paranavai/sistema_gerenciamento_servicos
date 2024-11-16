from typing import Set, Dict, List
from django.apps import apps as django_apps
from django.db import IntegrityError
from .enums import DjangoActions

class ModelFeatureGenerator:
    EXCLUDED_APPS = {'admin', 'contenttypes', 'sessions', 'auth'}
    
    FIXED_FEATURES = [
        ('clients_userviewset', 'Listar clientes do sistema'),
        ('providers_userviewset', 'Listar prestadores do sistema'),
        ('update_user_profile_userviewset', 'Atualizar perfil do usuário'),
        ('documents.download_document', 'Realizar download de documentos'),
        ('documents.preview_document', 'Visualizar preview de documentos'),
    ]
    
    def __init__(self):
        self.features: Set[str] = set()
        self.descriptions: Dict[str, str] = {}
        
    def generate_model_feature(self, app_label: str, model_name: str, action: DjangoActions) -> str:
        """Gera o nome da feature para um modelo e ação específicos"""
        return f"{app_label}.{action.value}_{model_name}"
        
    def add_fixed_features(self) -> None:
        """Adiciona as features fixas ao conjunto de features"""
        for name, description in self.FIXED_FEATURES:
            self.features.add(name)
            self.descriptions[name] = description
        
    def scan_models(self) -> None:
        """Escaneia todos os modelos do Django e gera as features correspondentes"""
        # Primeiro adiciona as features fixas
        self.add_fixed_features()
        
        # Depois escaneia os modelos
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

    def get_fixed_features(self, prefix: str = None) -> List[str]:
        """
        Retorna as features fixas, opcionalmente filtradas por prefixo
        
        Args:
            prefix: Prefixo para filtrar as features (ex: 'documents.')
        """
        features = [name for name, _ in self.FIXED_FEATURES]
        if prefix:
            features = [f for f in features if f.startswith(prefix)]
        return features

class DynamicFeatures:
    """Classe para gerenciar features dinâmicas e fixas do sistema"""
    
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
    
    def get_fixed_features(self, prefix: str = None) -> List[str]:
        return self._generator.get_fixed_features(prefix)
    
    def create_all_features(self) -> None:
        """Cria todas as features (dinâmicas e fixas) no banco de dados"""
        Feature = django_apps.get_model('core', 'Feature')
        
        # Criar/atualizar todas as features em uma única operação
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