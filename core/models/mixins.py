from django.db import models
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        

class DynamicModelPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        model_name = view.queryset.model._meta.model_name
        app_label = view.queryset.model._meta.app_label
        permission_name = f'{app_label}.{view.action}_{model_name}'
        return request.user.has_permission(permission_name)

class DynamicPermissionModelViewSet(ModelViewSet):
    permission_classes = [ DynamicModelPermissions]