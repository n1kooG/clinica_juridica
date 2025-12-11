from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    
    # Evita que se muestre el inline cuando se está creando un usuario nuevo
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 0
    
    # Solo mostrar el inline si el usuario ya existe
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs


class UserAdmin(BaseUserAdmin):
    inlines = []
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'get_sede', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__rol', 'perfil__sede')
    
    def get_inlines(self, request, obj=None):
        # Solo mostrar el inline de perfil si el usuario ya existe
        if obj:
            return [PerfilInline]
        return []
    
    def get_rol(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_rol_display()
        return '-'
    get_rol.short_description = 'Rol'
    
    def get_sede(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_sede_display()
        return '-'
    get_sede.short_description = 'Sede'


# Desregistrar el admin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)