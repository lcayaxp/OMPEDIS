from django.http import HttpResponseForbidden
from functools import wraps

# Decorador para permitir solo a la administrador
def administrador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'administrador':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    return _wrapped_view

# Decorador para permitir solo a los trabajadores
def trabajador_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'trabajador':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    return _wrapped_view
