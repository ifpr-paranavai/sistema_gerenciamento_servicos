from django.http import HttpResponseForbidden
from django.urls import resolve
from django.conf import settings
from authentication.models.user import User

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user') or not isinstance(request.user, User):
            return self.get_response(request)

        current_url = resolve(request.path_info).url_name
        required_permissions = getattr(settings, 'URL_PERMISSIONS', {}).get(current_url)

        if required_permissions:
            if isinstance(required_permissions, str):
                required_permissions = [required_permissions]
            
            for permission in required_permissions:
                if not request.user.has_permission(permission):
                    return HttpResponseForbidden(f"Permission '{permission}' required to access this page.")

        return self.get_response(request)