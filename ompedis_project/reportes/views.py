from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SesionTerapia
from .forms import SesionTerapiaForm
from django.db.models import Count, Func
from django.urls import reverse
from datetime import date
from django.db import models 

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
