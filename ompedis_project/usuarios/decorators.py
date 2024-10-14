from django.http import HttpResponseRedirect
from django.urls import reverse  # Para redirigir a una URL específica
from django.contrib import messages
from functools import wraps

# Decorador para permitir solo a la administrador
def administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'administrador':
            return view_func(request, *args, **kwargs)
        # Si no es administrador, mostrar mensaje de error y redirigir
        messages.error(request, "No tienes permiso para esta acción")
        return HttpResponseRedirect(reverse('dashboard'))  # Redirigir a la página principal o cualquier otra
    return _wrapped_view

# Decorador para permitir solo a los moderadores
def moderador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'moderador':
            return view_func(request, *args, **kwargs)
        # Si no es moderador, mostrar mensaje de error y redirigir
        messages.error(request, "No tienes permiso para esta acción")
        return HttpResponseRedirect(reverse('dashboard'))  # Cambia la URL según lo necesites
    return _wrapped_view

# Decorador para permitir solo a los usuarios
def usuario_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'usuario':
            return view_func(request, *args, **kwargs)
        # Si no es usuario, mostrar mensaje de error y redirigir
        messages.error(request, "No tienes permiso para esta acción")
        return HttpResponseRedirect(reverse('dashboard'))
    return _wrapped_view

# Decorador para permitir solo a moderadores o administradores
def moderador_o_administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol in ['moderador', 'administrador']:
            return view_func(request, *args, **kwargs)
        # Si no es moderador ni administrador, mostrar mensaje de error y redirigir
        messages.error(request, "No tienes permiso para esta acción")
        return HttpResponseRedirect(reverse('dashboard'))
    return _wrapped_view
