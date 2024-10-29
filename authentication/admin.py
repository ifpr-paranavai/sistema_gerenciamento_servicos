# authentication/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'cpf', 'is_active', 'role')
    list_filter = ('is_active', 'role')
    search_fields = ('email', 'name', 'cpf')
    ordering = ('email',)
    filter_horizontal = ('features',)

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Quando está criando um novo usuário
            return (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'name', 'cpf', 'password', 'role')
                }),
            )
        
        # Quando está editando um usuário existente
        return (
            (_('Personal info'), {'fields': ('email', 'name', 'cpf')}),
            (_('Permissions'), {'fields': ('is_active', 'role', 'features')}),
            (_('Profile'), {'fields': ('profile',)}),
        )

    def save_model(self, request, obj, form, change):
        if not change and 'password' in form.cleaned_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)