from django.http import HttpResponseForbidden
from core.models.role import Role

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                Role.objects.get(id=request.user.role.id)
            except Role.DoesNotExist:
                return HttpResponseForbidden("Você não tem um papel definido no sistema.")
        
        response = self.get_response(request)
        return response