from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.cuentas.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cuentas/', include('apps.cuentas.urls')),
    path('', include('apps.gestion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    
handler404 = 'apps.gestion.views.error_404'
handler403 = 'apps.gestion.views.error_403'
handler500 = 'apps.gestion.views.error_500'