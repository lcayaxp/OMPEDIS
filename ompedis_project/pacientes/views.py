from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Paciente, Municipio
from .forms import PacienteForm, ResponsableForm
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse
import json
import openpyxl
from django import forms

@method_decorator(login_required, name='dispatch')
class CrearPacienteView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'pacientes/crear_paciente.html'
    success_url = reverse_lazy('pacientes:lista_pacientes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['responsable_form'] = ResponsableForm(self.request.POST, prefix='responsable')
        else:
            context['responsable_form'] = ResponsableForm(prefix='responsable')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        responsable_form = context['responsable_form']
        if responsable_form.is_valid():
            paciente = form.save(commit=False)
            responsable = responsable_form.save()
            paciente.responsable = responsable
            paciente.save()
            if isinstance(form, ModelForm):
                form.save_m2m()  # Guarda las relaciones ManyToMany
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
class EditarPacienteView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'pacientes/editar_paciente.html'
    success_url = reverse_lazy('pacientes:lista_pacientes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['responsable_form'] = ResponsableForm(self.request.POST, prefix='responsable')
        else:
            paciente = self.get_object()
            responsable = paciente.responsables.first()  # Obtener el primer responsable asociado
            if responsable:
                context['responsable_form'] = ResponsableForm(instance=responsable, prefix='responsable')
            else:
                context['responsable_form'] = ResponsableForm(prefix='responsable')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        responsable_form = context['responsable_form']
        if responsable_form.is_valid():
            paciente = form.save(commit=False)
            responsable = responsable_form.save(commit=False)
            responsable.paciente = paciente  # Asocia el responsable al paciente
            responsable.save()
            paciente.save()
            if isinstance(form, forms.ModelForm):
                form.save_m2m()  # Guarda las relaciones ManyToMany
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

@login_required
def lista_pacientes_view(request):
    estado = request.GET.get('estado', 'activos')
    query = request.GET.get('q', '')
    if estado == 'inactivos':
        pacientes = Paciente.objects.filter(estado_activo=False)
    else:
        pacientes = Paciente.objects.filter(estado_activo=True)

    if query:
        pacientes = pacientes.filter(Q(nombre__icontains=query) | Q(apellido__icontains=query))

    context = {
        'pacientes': pacientes,
        'estado': estado,
        'query': query,
    }
    return render(request, 'pacientes/lista_pacientes.html', context)

@login_required
def cargar_municipios(request):
    departamento_id = request.GET.get('departamento')
    municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
    html = render_to_string('pacientes/municipios_dropdown_list_options.html', {'municipios': municipios})
    return HttpResponse(html)

@method_decorator(login_required, name='dispatch')
class PacienteDetailView(DetailView):
    model = Paciente
    template_name = 'pacientes/detalle_paciente.html'
    context_object_name = 'paciente'




@login_required
def confirmar_cambio_estado(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    context = {
        'paciente': paciente,
    }
    return render(request, 'pacientes/confirmar_cambio_estado.html', context)

@login_required
@require_POST
@csrf_exempt
def cambiar_estado_paciente_view(request):
    try:
        data = json.loads(request.body)
        paciente_id = data.get('id')
        nuevo_estado = data.get('estado') == 'activo'

        paciente = Paciente.objects.get(id=paciente_id)
        paciente.estado_activo = nuevo_estado
        paciente.save()

        # Filtrar los pacientes según el estado actual para actualizar la lista
        estado = request.GET.get('estado', 'activos')
        if estado == 'inactivos':
            pacientes = Paciente.objects.filter(estado_activo=False)
        else:
            pacientes = Paciente.objects.filter(estado_activo=True)

        query = request.GET.get('q', '')
        if query:
            pacientes = pacientes.filter(Q(nombre__icontains=query) | Q(apellido__icontains=query))

        context = {
            'pacientes': pacientes,
            'estado': estado,
            'query': query,
        }

        # Retornar la lista de pacientes actualizada
        return render(request, 'pacientes/lista_pacientes.html', context)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



@login_required
def exportar_pacientes_excel(request):
    estado = request.GET.get('estado', 'activos')
    if estado == 'inactivos':
        pacientes = Paciente.objects.filter(estado_activo=False)
    else:
        pacientes = Paciente.objects.filter(estado_activo=True)

    # Crear un libro de trabajo y una hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pacientes"

    # Escribir los encabezados
    headers = [
        'Nombre', 'Apellido', 'ID Partida Nacimiento', 'Fecha Nacimiento', 'Género', 'Estado Activo', 
        'Departamento', 'Municipio', 'Domicilio', 'Diagnóstico Médico', 'Medicamentos', 
        'Responsable Nombre', 'Responsable Apellido', 'Responsable Parentesco', 'Responsable Teléfono'
    ]
    ws.append(headers)

    # Escribir los datos de los pacientes
    for paciente in pacientes:
        responsable = paciente.responsables.first() if paciente.responsables.exists() else None
        ws.append([
            paciente.nombre,
            paciente.apellido,
            paciente.id_partida_nacimiento,
            paciente.fecha_nacimiento,
            paciente.genero,
            'Activo' if paciente.estado_activo else 'Inactivo',
            paciente.departamento.nombre if paciente.departamento else '',
            paciente.municipio.nombre if paciente.municipio else '',
            paciente.domicilio,
            paciente.diagnostico_medico,
            paciente.medicamentos,
            responsable.nombre if responsable else '',
            responsable.apellido if responsable else '',
            responsable.parentesco if responsable else '',
            responsable.telefono if responsable else ''
        ])

    # Crear una respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=pacientes_{estado}.xlsx'
    wb.save(response)
    return response