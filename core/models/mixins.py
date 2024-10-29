from django.db import models
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

class DynamicModelPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        model_name = view.queryset.model._meta.model_name
        app_label = view.queryset.model._meta.app_label
        permission_name = f'{app_label}.{view.action}_{model_name}'
        return request.user.has_permission(permission_name)

class DynamicPermissionModelViewSet(ModelViewSet):
    permission_classes = [ DynamicModelPermissions]

class DynamicViewPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        view_name = view.__class__.__name__.lower()
        action = view.action if hasattr(view, 'action') else request.method.lower()
        
        permission_name = f'{action}_{view_name}'
        return request.user.has_permission(permission_name)