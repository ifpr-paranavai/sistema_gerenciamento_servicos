from functools import wraps
from django.core.exceptions import PermissionDenied
from authentication.models.user import User
from core.models.feature import Feature

def has_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if hasattr(request, 'user'):
                user = User.objects.get(id=request.user.id)
                if user.role.features.filter(name=permission_name).exists():
                    return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator