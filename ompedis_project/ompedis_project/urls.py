"""
URL configuration for ompedis_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from usuarios.views import login_view, dashboard_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),  # Ruta principal para el login
    path('dashboard/', dashboard_view, name='dashboard'),  # Ruta para el dashboard
    path('usuarios/', include('usuarios.urls')),  # Incluye las URLs del app 'usuarios'
    path('pacientes/', include('pacientes.urls', namespace='pacientes')),  # Usando namespaces para evitar conflictos
    path('reportes/', include('reportes.urls')),  # Incluye las URLs del app 'reportes'
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Para servir archivos estáticos en desarrollo

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Para servir archivos multimedia en desarrollo




