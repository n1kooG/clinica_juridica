from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('personas/', views.personas_lista, name='personas_lista'),
    path('personas/nueva/', views.persona_crear, name='persona_crear'),
    path('personas/<int:pk>/editar/', views.persona_editar, name='persona_editar'),
    path('personas/<int:pk>/', views.persona_detalle, name='persona_detalle'),

    path('causas/', views.causas_lista, name='causas_lista'),
    path('causas/nueva/', views.causa_crear, name='causa_crear'),
    path('causas/<int:pk>/', views.causa_detalle, name='causa_detalle'),
    path('causas/<int:pk>/editar/', views.causa_editar, name='causa_editar'),
    path('causas/<int:pk>/linea-tiempo/', views.causa_linea_tiempo, name='causa_linea_tiempo'),
    path('causas/asociar-persona/', views.causa_persona_crear, name='causa_persona_crear'),
    path('causas/persona/<int:pk>/editar/', views.causa_persona_editar, name='causa_persona_editar'),
    path('causas/persona/<int:pk>/eliminar/', views.causa_persona_eliminar, name='causa_persona_eliminar'),


    path('audiencias/', views.audiencias_lista, name='audiencias_lista'),
    path('audiencias/nueva/', views.audiencia_crear, name='audiencia_crear'),
    path('audiencias/', views.audiencias_lista, name='audiencias_lista'),
    path('audiencias/crear/', views.audiencia_crear, name='audiencia_crear'),
    path('audiencias/<int:pk>/', views.audiencia_detalle, name='audiencia_detalle'),
    path('audiencias/<int:pk>/editar/', views.audiencia_editar, name='audiencia_editar'),

    path('documentos/', views.documentos_lista, name='documentos_lista'),
    path('documentos/crear/', views.documento_crear, name='documento_crear'),
    path('documentos/<int:pk>/', views.documento_detalle, name='documento_detalle'),

    path('relaciones/nueva/', views.causa_persona_crear, name='causa_persona_crear'),

    path('buscar/', views.buscar, name='buscar'),
    
    # Consentimientos
    path('consentimientos/', views.consentimientos_lista, name='consentimientos_lista'),
    path('consentimientos/nuevo/', views.consentimiento_crear, name='consentimiento_crear'),
    path('consentimientos/<int:pk>/', views.consentimiento_detalle, name='consentimiento_detalle'),
    path('consentimientos/<int:pk>/editar/', views.consentimiento_editar, name='consentimiento_editar'),
    path('consentimientos/<int:pk>/revocar/', views.consentimiento_revocar, name='consentimiento_revocar'),
    path('personas/<int:pk>/consentimientos/', views.persona_consentimientos, name='persona_consentimientos'),
    
    path('auditoria/', views.auditoria_lista, name='auditoria_lista'),
    path('auditoria/<int:pk>/', views.auditoria_detalle, name='auditoria_detalle'),
    
    path('calendario/', views.calendario, name='calendario'),
    
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/exportar-excel/', views.exportar_causas_excel, name='exportar_causas_excel'),
    path('reportes/exportar-pdf/', views.exportar_causas_pdf, name='exportar_causas_pdf'),
    
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.perfil_editar, name='perfil_editar'),
    path('perfil/cambiar-password/', views.perfil_cambiar_password, name='perfil_cambiar_password'),
    
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin-panel/usuarios/crear/', views.admin_usuario_crear, name='admin_usuario_crear'),
    path('admin-panel/usuarios/<int:pk>/editar/', views.admin_usuario_editar, name='admin_usuario_editar'),
    path('admin-panel/usuarios/<int:pk>/toggle/', views.admin_usuario_toggle, name='admin_usuario_toggle'),
    path('admin-panel/catalogos/<str:tipo>/', views.admin_catalogo, name='admin_catalogo'),
    path('admin-panel/catalogos/<str:tipo>/crear/', views.admin_catalogo_crear, name='admin_catalogo_crear'),
    path('admin-panel/catalogos/<str:tipo>/<int:pk>/editar/', views.admin_catalogo_editar, name='admin_catalogo_editar'),
    path('admin-panel/catalogos/<str:tipo>/<int:pk>/toggle/', views.admin_catalogo_toggle, name='admin_catalogo_toggle'),
    
    path('api/verificar-password/', views.verificar_password_fortaleza, name='verificar_password'),
]
