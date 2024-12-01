from django.db import models
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from django.utils import timezone
from django.db.models import ProtectedError
from rest_framework import status

  
class PersonalizedModelViewSet(ModelViewSet):
    
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValidationError as e:
           return Response({"detail": e.message} , status=status.HTTP_400_BAD_REQUEST)

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        abstract = True

    def delete(self):
        try:
            self.refresh_from_db()
            super().delete(keep_parents=True)
        except ProtectedError as e:
             raise ValidationError("Este registro não pode ser excluído pois está sendo usado em outro lugar.")
        
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

class DynamicPermissionModelViewSet(PersonalizedModelViewSet):
    permission_classes = [ DynamicModelPermissions]

class DynamicViewPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        view_name = view.__class__.__name__.lower()
        action = view.action if hasattr(view, 'action') else request.method.lower()
        
        permission_name = f'{action}_{view_name}'
        return request.user.has_permission(permission_name)