from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from core.models import Role

class PermissionRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        required_permission = view_kwargs.get('required_permission', None)

        if required_permission:
            user = request.user
            if not user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access this page.")
            
            # Verifica se o usuário possui a permissão necessária diretamente ou via sua Role
            if not user.has_permission(required_permission):
                return HttpResponseForbidden("You do not have permission to access this page.")

        return None
