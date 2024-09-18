from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from rest_framework.response import Response
from rest_framework import status

def permission_required(feature_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
                return HttpResponseForbidden("Authentication required.")
            
            if not request.user.has_permission(feature_name):
                if request.accepted_renderer.format == 'json':
                    return Response({"detail": f"Permission '{feature_name}' required."}, status=status.HTTP_403_FORBIDDEN)
                return HttpResponseForbidden(f"Permission '{feature_name}' required.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator