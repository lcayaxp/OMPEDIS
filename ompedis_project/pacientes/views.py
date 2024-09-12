from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Paciente, Municipio
from .forms import PacienteForm, ResponsableForm
from django.http import JsonResponse
from django.db.models import Q

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
            # Guarda el paciente y luego asocia el responsable
            paciente = form.save(commit=False)
            paciente.save()
            responsable = responsable_form.save(commit=False)
            responsable.paciente = paciente
            responsable.save()
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
        paciente = self.object
        if self.request.POST:
            context['responsable_form'] = ResponsableForm(self.request.POST, instance=paciente.responsables.first(), prefix='responsable')
        else:
            context['responsable_form'] = ResponsableForm(instance=paciente.responsables.first(), prefix='responsable')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        responsable_form = context['responsable_form']
        if responsable_form.is_valid():
            paciente = form.save()  # Guarda el paciente
            responsable = responsable_form.save(commit=False)
            responsable.paciente = paciente  # Asocia el responsable con el paciente
            responsable.save()  # Guarda el responsable
            return super().form_valid(form)
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
    departamento_id = request.GET.get('departamento_id')
    if departamento_id:
        municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
        return JsonResponse(list(municipios.values('id', 'nombre')), safe=False)
    return JsonResponse({'error': 'No se proporcionó un departamento válido'}, status=400)

@method_decorator(login_required, name='dispatch')
class PacienteDetailView(DetailView):
    model = Paciente
    template_name = 'pacientes/detalle_paciente.html'
    context_object_name = 'paciente'
