from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db.models import Count, Func
from django.db import models
from datetime import date
from io import BytesIO
from base64 import b64decode

from .models import SesionTerapia
from .forms import SesionTerapiaForm, ReporteGeneracionForm

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.chart import BarChart, Reference, PieChart
from collections import Counter
from datetime import datetime, timedelta

from PIL import Image as PILImage
from django.core.files.base import ContentFile
import io
import json

# Vistas que utilicen estos imports se pueden definir a continuación


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
        'fecha_inicio': fecha_inicio,  # Añadir fecha_inicio al contexto
        'fecha_fin': fecha_fin,  # Añadir fecha_fin al contexto
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
                    'Masculino' if sesion.genero == 'Masculino' else 'Femenino'
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
def exportar_excel_view(request):
    # Filtrar las sesiones
    sesiones = SesionTerapia.objects.all()

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            sesiones = sesiones.filter(fecha_sesion__gte=fecha_inicio)
        except ValueError:
            pass  # Manejar el error de formato de fecha si es necesario

    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            sesiones = sesiones.filter(fecha_sesion__lte=fecha_fin)
        except ValueError:
            pass  # Manejar el error de formato de fecha si es necesario

    # Crear un archivo Excel en memoria
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Sesiones de Terapia'

    # Crear encabezados con formato
    headers = ['No.', 'Nombre', 'Diagnóstico', 'Sexo', 'Edad', 'Área', 'Fecha de Ingreso']
    sheet.append(headers)
    
    header_fill = PatternFill(start_color="B0C4DE", end_color="B0C4DE", fill_type="solid")
    header_font = Font(bold=True)
    
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        sheet.column_dimensions[get_column_letter(col_num)].width = 20

    # Agregar datos
    for idx, sesion in enumerate(sesiones, start=2):
        edad = (datetime.now().date() - sesion.paciente.fecha_nacimiento).days // 365
        data = [
            idx - 1,
            f"{sesion.paciente.nombre} {sesion.paciente.apellido}",
            sesion.diagnostico,
            'Masculino' if sesion.genero == 'Masculino' else 'Femenino',
            edad,
            sesion.area,
            sesion.fecha_sesion.strftime('%Y-%m-%d')
        ]
        sheet.append(data)
    
    # Aplicar alineación a todas las celdas de la tabla
    for row in sheet.iter_rows(min_row=2, max_row=len(sesiones) + 1, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # Contar pacientes por género
    genero_count = Counter(sesion.genero for sesion in sesiones)

    # Calcular el rango de edades de los pacientes
    edades = [((datetime.now().date() - sesion.paciente.fecha_nacimiento).days // 365) for sesion in sesiones]
    rango_edades = Counter((edad // 10) * 10 for edad in edades)

    # Contar terapias por semana
    terapias_por_semana = Counter((sesion.fecha_sesion - timedelta(days=sesion.fecha_sesion.weekday())).strftime('%Y-%m-%d') for sesion in sesiones)

    # Agregar el resumen de género
    start_row = len(sesiones) + 3
    sheet.append(['Total pacientes femeninos y masculinos'])
    sheet.append(['Femenino', genero_count.get('Femenino', 0)])
    sheet.append(['Masculino', genero_count.get('Masculino', 0)])
    total_pacientes = genero_count.get('Femenino', 0) + genero_count.get('Masculino', 0)
    sheet.append(['Total', total_pacientes])
    
    # Aplicar formato
    for row in sheet.iter_rows(min_row=start_row, max_row=start_row + 3, min_col=1, max_col=2):
        for cell in row:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')

    # Crear el gráfico de barras para género
    chart_genero = BarChart()
    data_genero = Reference(sheet, min_col=2, min_row=start_row + 1, max_row=start_row + 2)
    categories_genero = Reference(sheet, min_col=1, min_row=start_row + 1, max_row=start_row + 2)
    chart_genero.add_data(data_genero, titles_from_data=False)
    chart_genero.set_categories(categories_genero)
    chart_genero.title = "Total pacientes femeninos y masculinos"
    chart_genero.x_axis.title = "Sexo"
    chart_genero.y_axis.title = "Total"
    sheet.add_chart(chart_genero, f"E{start_row}")

    # Agregar el resumen del rango de edades
    start_row_edades = start_row + 5
    sheet.append(['Edades', 'Cantidad'])
    for rango, count in rango_edades.items():
        sheet.append([f"{rango} - {rango + 9} años", count])
    sheet.append(['Total', len(sesiones)])

    # Aplicar formato
    for row in sheet.iter_rows(min_row=start_row_edades + 1, max_row=start_row_edades + len(rango_edades) + 1, min_col=1, max_col=2):
        for cell in row:
            cell.alignment = Alignment(horizontal='center')

    # Crear el gráfico de pastel (torta) para el rango de edades
    chart_edades = PieChart()
    data_edades = Reference(sheet, min_col=2, min_row=start_row_edades + 1, max_row=start_row_edades + len(rango_edades))
    categories_edades = Reference(sheet, min_col=1, min_row=start_row_edades + 1, max_row=start_row_edades + len(rango_edades))
    chart_edades.add_data(data_edades, titles_from_data=False)
    chart_edades.set_categories(categories_edades)
    chart_edades.title = "Rango de edades de pacientes atendidos en Ompedis Ostuncalco"
    sheet.add_chart(chart_edades, f"E{start_row_edades}")

    # Agregar el resumen de terapias por semana
    start_row_terapias = start_row_edades + len(rango_edades) + 5
    sheet.append(['Semana', 'Sesiones Realizadas'])
    for semana, count in terapias_por_semana.items():
        sheet.append([semana, count])
    total_terapias = sum(terapias_por_semana.values())
    sheet.append(['Total', total_terapias])

    # Aplicar formato
    for row in sheet.iter_rows(min_row=start_row_terapias + 1, max_row=start_row_terapias + len(terapias_por_semana) + 1, min_col=1, max_col=2):
        for cell in row:
            cell.alignment = Alignment(horizontal='center')

    # Crear el gráfico de barras para terapias por semana
    chart_terapias = BarChart()
    data_terapias = Reference(sheet, min_col=2, min_row=start_row_terapias + 1, max_row=start_row_terapias + len(terapias_por_semana))
    categories_terapias = Reference(sheet, min_col=1, min_row=start_row_terapias + 1, max_row=start_row_terapias + len(terapias_por_semana))
    chart_terapias.add_data(data_terapias, titles_from_data=False)
    chart_terapias.set_categories(categories_terapias)
    chart_terapias.title = "Total de terapias dadas a pacientes atendidos por semana en el mes "
    chart_terapias.x_axis.title = "Semana"
    chart_terapias.y_axis.title = "Sesiones Realizadas"
    sheet.add_chart(chart_terapias, f"E{start_row_terapias}")

    # Crear un archivo en memoria para guardar el workbook
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=estadisticas_sesiones_terapia.xlsx'
    workbook.save(response)
    return response