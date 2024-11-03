from django.contrib import admin

from documents.models.document import Document
from documents.models.document_template import DocumentTemplate, ServiceDocumentRequirement

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'file_type', 'document_type', 'created_at')
    list_filter = ('document_type', 'file_type', 'created_at')
    search_fields = ('file_name', 'document_type')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'file_types', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'file_types')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ServiceDocumentRequirement)
class ServiceDocumentRequirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'document_template', 'is_required', 'created_at', 'updated_at')
    list_filter = ('is_required', 'created_at', 'updated_at')
    search_fields = ('service__name', 'document_template__name')
    readonly_fields = ('created_at', 'updated_at')