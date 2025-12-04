from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cuentas/', include('apps.cuentas.urls')),
    path('', include('apps.gestion.urls')),
]
