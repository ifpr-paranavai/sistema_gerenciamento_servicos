from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.api.document_template_view import DocumentTemplateViewSet, ServiceDocumentRequirementViewSet
from documents.api.document_view import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'document-templates', DocumentTemplateViewSet)
router.register(r'service-document-requirements', ServiceDocumentRequirementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]