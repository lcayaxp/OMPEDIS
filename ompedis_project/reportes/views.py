from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SesionTerapia
from .forms import SesionTerapiaForm
from django.db.models import Count, Func
from django.urls import reverse
from datetime import date
from django.db import models 
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from django.http import FileResponse
from .forms import ReporteGeneracionForm
import openpyxl
from openpyxl.utils import get_column_letter
from PIL import Image as PILImage
from base64 import b64decode
from django.core.files.base import ContentFile
from PIL import Image
import io
import json
from django.http import JsonResponse

@login_required
def menu_reportes_view(request):
    return render(request, 'reportes/menu_reportes.html')

# Definición de la clase Week para usar EXTRACT en PostgreSQL
class Week(Func):
    function = 'EXTRACT'
    template = "%(function)s('week' FROM %(expressions)s)"
    output_field = models.FloatField()  # Especificar el tipo de campo de salida

@login_required
def registrar_sesion_view(request):
    if request.method == 'POST':
        form = SesionTerapiaForm(request.POST)
        if form.is_valid():
            sesion = form.save(commit=False)
            sesion.genero = sesion.paciente.genero  # Asignar el género desde el paciente seleccionado
            sesion.save()
            # Aquí añadimos el mensaje de éxito
            return render(request, 'reportes/registrar_sesion.html', {
                'form': SesionTerapiaForm(),  # Nuevo formulario
                'success_message': 'Se registró la sesión de terapia con éxito'
            })
        else:
            print(form.errors)  # Esto ayudará a identificar otros errores si existen
    else:
        form = SesionTerapiaForm()

    context = {
        'form': form,
    }
    return render(request, 'reportes/registrar_sesion.html', context)
    
@login_required
def ver_estadisticas_view(request):
    # Filtrar todas las sesiones de terapia con filtros de fecha
    sesiones = SesionTerapia.objects.all()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        sesiones = sesiones.filter(fecha_sesion__gte=fecha_inicio)
    if fecha_fin:
        sesiones = sesiones.filter(fecha_sesion__lte=fecha_fin)

    # Calcular rangos de edad para los pacientes
    rangos_edad = {
        '0_18': sum(1 for sesion in sesiones if sesion.paciente.calcular_edad() <= 18),
        '19_35': sum(1 for sesion in sesiones if 19 <= sesion.paciente.calcular_edad() <= 35),
        '36_60': sum(1 for sesion in sesiones if 36 <= sesion.paciente.calcular_edad() <= 60),
        '60_plus': sum(1 for sesion in sesiones if sesion.paciente.calcular_edad() > 60),
    }

    # Contar el total de pacientes femeninos y masculinos
    total_femeninos = sesiones.filter(genero='Femenino').count()
    total_masculinos = sesiones.filter(genero='Masculino').count()

    # Obtener el número de terapias por semana
    terapias_por_semana = sesiones.annotate(
        week=Week('fecha_sesion')
    ).values('week').annotate(total=Count('id')).order_by('week')

    # Pasar los datos al contexto
    context = {
        'total_femeninos': total_femeninos,
        'total_masculinos': total_masculinos,
        'rangos_edad': rangos_edad,
        'terapias_por_semana': terapias_por_semana,
        'sesiones': sesiones,  # Añadir las sesiones al contexto para la tabla
    }

    return render(request, 'reportes/ver_estadisticas.html', context)

@login_required
def ver_listado_sesiones_view(request):
    sesiones = SesionTerapia.objects.all()

    context = {
        'sesiones': sesiones,
    }
    return render(request, 'reportes/listado_sesiones.html', context)

@login_required
def generar_reporte_view(request):
    if request.method == 'POST':
        form = ReporteGeneracionForm(request.POST)
        if form.is_valid():
            # Filtrar sesiones de terapia con los parámetros del formulario
            sesiones = SesionTerapia.objects.all()

            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            paciente = form.cleaned_data['paciente']

            if fecha_inicio:
                sesiones = sesiones.filter(fecha_sesion__gte=fecha_inicio)
            if fecha_fin:
                sesiones = sesiones.filter(fecha_sesion__lte=fecha_fin)
            if paciente:
                sesiones = sesiones.filter(paciente=paciente)

            # Crear buffer
            buffer = BytesIO()

            # Crear el PDF
            pdf = SimpleDocTemplate(buffer, pagesize=A4)

            # Estilos de texto y elementos
            styles = getSampleStyleSheet()
            title_style = styles["Title"]
            normal_style = styles["BodyText"]

            # Contenido del PDF
            content = []

            # Encabezado
            content.append(Paragraph("Reporte de Actividades", title_style))
            content.append(Spacer(1, 12))

            # Mostrar nombre completo del paciente si está seleccionado
            if paciente:
                nombre_completo = f"{paciente.nombre} {paciente.apellido or ''} {paciente.nombre} {paciente.apellido or ''}".strip()
                content.append(Paragraph(f"Paciente: {nombre_completo}", normal_style))
                content.append(Spacer(1, 12))

            # Añadir información general
            content.append(Paragraph("Este informe resume las actividades realizadas durante las sesiones de terapia.", normal_style))
            content.append(Spacer(1, 12))

            # Crear tabla de datos dinámicamente a partir de las sesiones filtradas
            data = [['Fecha', 'Diagnóstico', 'Área', 'Género']]  # Encabezados de la tabla

            for sesion in sesiones:
                data.append([
                    sesion.fecha_sesion.strftime('%Y-%m-%d'),
                    sesion.diagnostico,
                    sesion.area,
                    'Masculino' if sesion.genero == 'M' else 'Femenino'
                ])

            # Estilo para la tabla
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])

            table = Table(data)
            table.setStyle(table_style)

            content.append(table)
            content.append(Spacer(1, 12))

            # Firma final o pie de página
            content.append(Spacer(1, 48))
            content.append(Paragraph("Este reporte fue generado automáticamente por el sistema OMPEDIS.", normal_style))

            # Construir PDF
            pdf.build(content)

            # Enviar PDF como respuesta
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename='reporte_formal.pdf')
    else:
        form = ReporteGeneracionForm()

    return render(request, 'reportes/generar_reporte.html', {'form': form})

@login_required
def exportar_pdf_view(request):
    if request.method == 'POST':
        try:
            # Capturar los datos enviados desde el frontend
            data = json.loads(request.body)
            gender_chart_data = data.get('gender_chart')
            age_range_chart_data = data.get('age_range_chart')
            weekly_therapies_chart_data = data.get('weekly_therapies_chart')

            # Verificar que los datos no sean None
            if not gender_chart_data or not age_range_chart_data or not weekly_therapies_chart_data:
                return JsonResponse({"error": "Faltan gráficos para generar el PDF."}, status=400)

            # Decodificar las imágenes base64
            gender_chart_img = PILImage.open(io.BytesIO(b64decode(gender_chart_data.split(',')[1])))
            age_range_chart_img = PILImage.open(io.BytesIO(b64decode(age_range_chart_data.split(',')[1])))
            weekly_therapies_chart_img = PILImage.open(io.BytesIO(b64decode(weekly_therapies_chart_data.split(',')[1])))

            # Crear el PDF
            buffer = io.BytesIO()
            pdf = SimpleDocTemplate(buffer, pagesize=A4)

            elements = []

            # Añadir las imágenes al PDF
            charts = [
                gender_chart_img,
                age_range_chart_img,
                weekly_therapies_chart_img
            ]

            for chart in charts:
                img_buffer = io.BytesIO()
                chart.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                reportlab_img = Image(img_buffer)
                reportlab_img.drawHeight = 3 * inch  # Ajusta el tamaño de la imagen
                reportlab_img.drawWidth = 6 * inch
                elements.append(reportlab_img)

            # Construir el PDF
            pdf.build(elements)

            # Enviar el PDF como respuesta
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename='reportes_con_graficas.pdf')

        except Exception as e:
            # Capturar cualquier error y devolver una respuesta JSON con el error
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)

    # Si el método no es POST, devolvemos un error
    return JsonResponse({"error": "Método no permitido."}, status=405)
@login_required
def exportar_excel_view(request):
    # Filtrar las sesiones
    sesiones = SesionTerapia.objects.all()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        sesiones = sesiones.filter(fecha_sesion__gte=fecha_inicio)
    if fecha_fin:
        sesiones = sesiones.filter(fecha_sesion__lte=fecha_fin)

    # Crear un archivo Excel en memoria
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sesiones de Terapia'

    # Crear encabezados
    headers = ['Fecha', 'Paciente', 'Diagnóstico', 'Área', 'Género']
    sheet.append(headers)

    # Agregar datos
    for sesion in sesiones:
        sheet.append([
            sesion.fecha_sesion.strftime('%Y-%m-%d'),
            f"{sesion.paciente.nombre} {sesion.paciente.apellido}",
            sesion.diagnostico,
            sesion.area,
            'Masculino' if sesion.genero == 'M' else 'Femenino'
        ])

    # Ajustar el ancho de las columnas
    for col in range(1, len(headers) + 1):
        sheet.column_dimensions[get_column_letter(col)].width = 20

    # Crear un archivo en memoria
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=estadisticas_sesiones_terapia.xlsx'

    workbook.save(response)
    return response