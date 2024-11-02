from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Sistema Gerenciamento de Serviços API",
        default_version='v1',
        description="Engenharia de Software 2024 - TCC",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('api/v1/authentication/', include('authentication.urls')),
    path('api/v1/user/', include('authentication.user_urls')),
    path('api/v1/appointment/', include('appointment.urls')),
    path('api/v1/service/', include('service.urls')),
    path('api/v1/core/', include('core.urls')),
    path('api/v1/documents/', include('documents.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
