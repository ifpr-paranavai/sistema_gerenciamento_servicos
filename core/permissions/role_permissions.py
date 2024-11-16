from dataclasses import dataclass
from typing import List
from .enums import (
    MenuFeatures, HomeFeatures, ProfileFeatures, TechnicalFeatures,
    DocumentFeatures, AppointmentFeatures, MessageFeatures, ServiceFeatures
)

@dataclass
class FeatureGroup:
    name: str
    features: List[str]
    description: str = ""

ROLE_PERMISSIONS = {
    'client': FeatureGroup(
        name="Client Permissions",
        features=[
            # Menu Features
            MenuFeatures.CAN_SHOW_APPOINTMENTS_MENU,
            MenuFeatures.CAN_SHOW_MESSAGES_MENU,
            MenuFeatures.CAN_SHOW_CLIENTS_MENU,
            # Home Features
            HomeFeatures.CAN_SHOW_HOME_DEFAULT,
            # Profile Features
            ProfileFeatures.CAN_UPDATE_PROFILE,
            # Document Features
            DocumentFeatures.PREVIEW,
            # Appointment Features
            AppointmentFeatures.LIST,
            AppointmentFeatures.RETRIEVE,
            AppointmentFeatures.CREATE,
            AppointmentFeatures.UPDATE,
            # Message Features
            MessageFeatures.LIST,
            MessageFeatures.CREATE,
        ]
    ),
    'provider': FeatureGroup(
        name="Provider Permissions",
        features=[
            # Menu Features
            MenuFeatures.CAN_SHOW_APPOINTMENTS_MENU,
            MenuFeatures.CAN_SHOW_MESSAGES_MENU,
            MenuFeatures.CAN_SHOW_DOCUMENTS_MENU,
            MenuFeatures.CAN_SHOW_SERVICES_MENU,
            MenuFeatures.CAN_SHOW_PROVIDERS_MENU,
            # Home Features
            HomeFeatures.CAN_SHOW_HOME_DASHBOARDS,
            # Profile and Technical Features
            ProfileFeatures.CAN_UPDATE_PROFILE,
            TechnicalFeatures.CAN_SHOW_DIAGRAM_UML,
            # Document Features
            DocumentFeatures.DOWNLOAD,
            DocumentFeatures.PREVIEW,
            # Appointment Features
            AppointmentFeatures.LIST,
            AppointmentFeatures.RETRIEVE,
            AppointmentFeatures.UPDATE,
            AppointmentFeatures.PARTIAL_UPDATE,
            # Service Features
            ServiceFeatures.LIST,
            ServiceFeatures.CREATE,
            ServiceFeatures.UPDATE,
            # Message Features
            MessageFeatures.LIST,
            MessageFeatures.CREATE,
        ]
    )
}