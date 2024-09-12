from django.urls import path
from .views import menu_reportes_view, registrar_sesion_view, ver_estadisticas_view, ver_listado_sesiones_view, ver_estadisticas_graficas_view

urlpatterns = [
    path('', menu_reportes_view, name='menu_reportes'),
    path('registrar-sesion/', registrar_sesion_view, name='registrar_sesion'),
    path('estadisticas/', ver_estadisticas_view, name='ver_estadisticas'),
    path('estadisticas/listado-sesiones/', ver_listado_sesiones_view, name='listado_sesiones'),
    path('estadisticas/graficas/', ver_estadisticas_graficas_view, name='estadisticas_graficas'),
]
