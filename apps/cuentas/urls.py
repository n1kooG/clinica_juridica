from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
]
