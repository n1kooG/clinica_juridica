from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_rol', 'get_sede', 'is_active']
    list_filter = BaseUserAdmin.list_filter + ('perfil__rol', 'perfil__sede',)

    def get_rol(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_rol_display()
        return '-'
    get_rol.short_description = 'Rol'

    def get_sede(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_sede_display() if obj.perfil.sede else '-'
        return '-'
    get_sede.short_description = 'Sede'


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)