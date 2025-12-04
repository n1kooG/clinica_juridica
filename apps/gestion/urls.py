from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('personas/', views.personas_lista, name='personas_lista'),
    path('personas/nueva/', views.persona_crear, name='persona_crear'),
    path('personas/<int:pk>/editar/', views.persona_editar, name='persona_editar'),

    path('causas/', views.causas_lista, name='causas_lista'),
    path('causas/nueva/', views.causa_crear, name='causa_crear'),
    path('causas/<int:pk>/', views.causa_detalle, name='causa_detalle'),
    path('causas/<int:pk>/editar/', views.causa_editar, name='causa_editar'),

    path('audiencias/', views.audiencias_lista, name='audiencias_lista'),
    path('audiencias/nueva/', views.audiencia_crear, name='audiencia_crear'),

    path('documentos/', views.documentos_lista, name='documentos_lista'),
    path('documentos/nuevo/', views.documento_crear, name='documento_crear'),

    path('relaciones/nueva/', views.causa_persona_crear, name='causa_persona_crear'),

    path('buscar/', views.buscar, name='buscar'),
]
