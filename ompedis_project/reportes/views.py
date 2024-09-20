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
            return redirect('reportes:menu_reportes')
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
    return render(request, 'reportes/ver_estadisticas.html')

@login_required
def ver_listado_sesiones_view(request):
    sesiones = SesionTerapia.objects.all()

    context = {
        'sesiones': sesiones,
    }
    return render(request, 'reportes/listado_sesiones.html', context)

@login_required
def ver_estadisticas_graficas_view(request):
    today = date.today()

    # Filtrar sesiones de terapia por rangos de edad calculando la edad del paciente en Python
    sesiones = SesionTerapia.objects.all()
    
    rangos_edad = {
        '0_18': sum(1 for sesion in sesiones if sesion.paciente.calcular_edad() <= 18),
        '19_35': sum(1 for sesion in sesiones if 19 <= sesion.paciente.calcular_edad() <= 35),
        '36_60': sum(1 for sesion in sesiones if 36 <= sesion.paciente.calcular_edad() <= 60),
        '60_plus': sum(1 for sesion in sesiones if sesion.paciente.calcular_edad() > 60),
    }

    total_femeninos = SesionTerapia.objects.filter(genero='F').count()
    total_masculinos = SesionTerapia.objects.filter(genero='M').count()

    terapias_por_semana = SesionTerapia.objects.annotate(
        week=Week('fecha_sesion')
    ).values('week').annotate(total=Count('id')).order_by('week')

    context = {
        'total_femeninos': total_femeninos,
        'total_masculinos': total_masculinos,
        'rangos_edad': rangos_edad,
        'terapias_por_semana': terapias_por_semana,
    }

    return render(request, 'reportes/estadisticas_graficas.html', context)

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

