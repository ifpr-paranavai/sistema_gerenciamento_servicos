from enum import Enum

class DjangoActions(str, Enum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    UPDATE = "update"
    PARTIAL_UPDATE = "partial_update"
    DESTROY = "destroy"

class MenuFeatures(str, Enum):
    CAN_SHOW_APPOINTMENTS_MENU = "CAN_SHOW_APPOINTMENTS_MENU"
    CAN_SHOW_MESSAGES_MENU = "CAN_SHOW_MESSAGES_MENU"
    CAN_SHOW_DOCUMENTS_MENU = "CAN_SHOW_DOCUMENTS_MENU"
    CAN_SHOW_SERVICES_MENU = "CAN_SHOW_SERVICES_MENU"
    CAN_SHOW_CLIENTS_MENU = "CAN_SHOW_CLIENTS_MENU"
    CAN_SHOW_PROVIDERS_MENU = "CAN_SHOW_PROVIDERS_MENU"

class HomeFeatures(str, Enum):
    CAN_SHOW_HOME_DASHBOARDS = "CAN_SHOW_HOME_DASHBOARDS"
    CAN_SHOW_HOME_DEFAULT = "CAN_SHOW_HOME_DEFAULT"

class ProfileFeatures(str, Enum):
    CAN_UPDATE_PROFILE = "CAN_UPDATE_PROFILE"

class TechnicalFeatures(str, Enum):
    CAN_SHOW_DIAGRAM_UML = "CAN_SHOW_DIAGRAM_UML"

class DocumentFeatures(str, Enum):
    DOWNLOAD = "documents.download_document"
    PREVIEW = "documents.preview_document"

class AppointmentFeatures(str, Enum):
    LIST = "appointments.list_appointment"
    RETRIEVE = "appointments.retrieve_appointment"
    CREATE = "appointments.create_appointment"
    UPDATE = "appointments.update_appointment"
    PARTIAL_UPDATE = "appointments.partial_update_appointment"

class MessageFeatures(str, Enum):
    LIST = "messages.list_message"
    CREATE = "messages.create_message"

class ServiceFeatures(str, Enum):
    LIST = "services.list_service"
    CREATE = "services.create_service"
    UPDATE = "services.update_service"
    
class RoleTypes(str, Enum):
    CLIENT = "client"
    PROVIDER = "provider"