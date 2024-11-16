# core/permissions/descriptions.py
from .enums import (
    MenuFeatures, 
    HomeFeatures, 
    ProfileFeatures, 
    TechnicalFeatures,
    DocumentFeatures, 
    AppointmentFeatures, 
    MessageFeatures, 
    ServiceFeatures
)

FEATURE_DESCRIPTIONS = {
    # Menu Features
    MenuFeatures.CAN_SHOW_APPOINTMENTS_MENU: "Permite visualizar o menu de agendamentos no sistema",
    MenuFeatures.CAN_SHOW_MESSAGES_MENU: "Permite visualizar o menu de mensagens no sistema",
    MenuFeatures.CAN_SHOW_DOCUMENTS_MENU: "Permite visualizar o menu de documentos no sistema",
    MenuFeatures.CAN_SHOW_SERVICES_MENU: "Permite visualizar o menu de serviços no sistema",
    MenuFeatures.CAN_SHOW_CLIENTS_MENU: "Permite visualizar o menu de clientes no sistema",
    MenuFeatures.CAN_SHOW_PROVIDERS_MENU: "Permite visualizar o menu de prestadores de serviço no sistema",
    
    # Home Features
    HomeFeatures.CAN_SHOW_HOME_DASHBOARDS: "Permite visualizar os dashboards na página inicial",
    HomeFeatures.CAN_SHOW_HOME_DEFAULT: "Permite visualizar a página inicial padrão do sistema",
    
    # Profile Features
    ProfileFeatures.CAN_UPDATE_PROFILE: "Permite atualizar informações do próprio perfil",
    
    # Technical Features
    TechnicalFeatures.CAN_SHOW_DIAGRAM_UML: "Permite visualizar diagramas UML do sistema",
    
    # Document Features
    DocumentFeatures.DOWNLOAD: "Permite realizar download de documentos no sistema",
    DocumentFeatures.PREVIEW: "Permite visualizar preview de documentos no sistema",
    
    # Appointment Features
    AppointmentFeatures.LIST: "Permite listar todos os agendamentos disponíveis",
    AppointmentFeatures.RETRIEVE: "Permite visualizar detalhes de um agendamento específico",
    AppointmentFeatures.CREATE: "Permite criar novos agendamentos no sistema",
    AppointmentFeatures.UPDATE: "Permite atualizar informações de agendamentos existentes",
    AppointmentFeatures.PARTIAL_UPDATE: "Permite atualizar parcialmente informações de agendamentos",
    
    # Message Features
    MessageFeatures.LIST: "Permite listar todas as mensagens disponíveis",
    MessageFeatures.CREATE: "Permite enviar novas mensagens no sistema",
    
    # Service Features
    ServiceFeatures.LIST: "Permite listar todos os serviços cadastrados",
    ServiceFeatures.CREATE: "Permite criar novos serviços no sistema",
    ServiceFeatures.UPDATE: "Permite atualizar informações de serviços existentes",

    # Feature Groups - Descrições para grupos de permissões
    'client_group': "Grupo de permissões para clientes do sistema",
    'provider_group': "Grupo de permissões para prestadores de serviço",
    
    # Dynamic Features - Descrição padrão para features dinâmicas
    'dynamic_feature': "Permissão gerada automaticamente para {action} {model}",
    
    # System Features - Descrições para ações do sistema
    'system_feature': "Permissão do sistema para {action}"
}

def get_feature_description(feature_key: str, default: str = None) -> str:
    """
    Obtém a descrição de uma feature com fallback para descrição padrão
    
    Args:
        feature_key: Chave da feature
        default: Descrição padrão caso não encontre
        
    Returns:
        str: Descrição da feature
    """
    return FEATURE_DESCRIPTIONS.get(
        feature_key,
        default or f"Permissão para {feature_key}"
    )

def get_dynamic_feature_description(action: str, model: str) -> str:
    """
    Gera descrição para features dinâmicas
    
    Args:
        action: Ação da feature (list, create, etc)
        model: Nome do modelo
        
    Returns:
        str: Descrição gerada
    """
    template = FEATURE_DESCRIPTIONS['dynamic_feature']
    return template.format(action=action, model=model)

def get_system_feature_description(action: str) -> str:
    """
    Gera descrição para features do sistema
    
    Args:
        action: Ação do sistema
        
    Returns:
        str: Descrição gerada
    """
    template = FEATURE_DESCRIPTIONS['system_feature']
    return template.format(action=action)