from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'cpf', 'is_active', 'role')
    list_filter = ('is_active', 'role')
    fieldsets = (
        (_('Personal info'), {'fields': ('email', 'name', 'cpf')}),
        (_('Permissions'), {'fields': ('is_active', 'role', 'features')}),
        (_('Profile'), {'fields': ('profile',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'cpf', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name', 'cpf')
    ordering = ('email',)
    filter_horizontal = ('features',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

admin.site.register(User, UserAdmin)