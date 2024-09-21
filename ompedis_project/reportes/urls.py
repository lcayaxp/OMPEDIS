from django.urls import path
from .views import registrar_sesion_view, ver_estadisticas_view, ver_listado_sesiones_view
from .views import generar_reporte_view, exportar_pdf_view, exportar_excel_view

urlpatterns = [
    path('registrar-sesion/', registrar_sesion_view, name='registrar_sesion'),
    path('estadisticas/', ver_estadisticas_view, name='ver_estadisticas'),
    path('estadisticas/listado-sesiones/', ver_listado_sesiones_view, name='listado_sesiones'),
    path('reportes/generar/', generar_reporte_view, name='generar_reporte'),
    path('exportar-pdf/', exportar_pdf_view, name='exportar_pdf'),
    path('exportar-excel/', exportar_excel_view, name='exportar_excel'),


]
