from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin  # Importación corregida
from .models import CustomUser
from .forms import PerfilUsuarioForm, UsuarioCreationForm, UsuarioChangeForm
from .decorators import administrador_required, moderador_required, usuario_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomAuthenticationForm
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


# Vista para el login
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')  # Mensaje de éxito
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales inválidas, intente nuevamente.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

# Vista del dashboard solo accesible por la administrador
@login_required
def dashboard_view(request):
    return render(request, 'usuarios/dashboard.html')

# Vista para listar pacientes, accesible solo para trabajadores
@login_required
@moderador_required
def lista_pacientes_view(request):
    return render(request, 'pacientes/lista_pacientes.html')

# Vista para editar el perfil de usuario
@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user)
    return render(request, 'usuarios/perfil.html', {'form': form})

# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')  # Mensaje de éxito
    return redirect('login')

# Vista para registrar un nuevo usuario
@method_decorator(administrador_required, name='dispatch')
class SignUpView(CreateView):
    form_class = UsuarioCreationForm
    success_url = reverse_lazy('user_list')
    template_name = 'usuarios/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario registrado exitosamente.')  # Mensaje de éxito
        return response

@method_decorator(administrador_required, name='dispatch')
# Vista para listar usuarios
class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'usuarios/user_list.html'
    context_object_name = 'users'

@method_decorator(administrador_required, name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UsuarioChangeForm
    template_name = 'usuarios/user_update.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario actualizado exitosamente.')  # Mensaje de éxito
        return response

@method_decorator(administrador_required, name='dispatch')
class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = CustomUser
    template_name = 'usuarios/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    success_message = "El usuario fue eliminado exitosamente."

class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'usuarios/user_detail.html'
    context_object_name = 'user'


# Vistas para la recuperación de contraseña
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'usuarios/password_reset_sent.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'usuarios/password_reset_form.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'usuarios/password_reset_done.html'