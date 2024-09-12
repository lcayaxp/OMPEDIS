from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UsuarioCreationForm, UsuarioChangeForm
from .models import CustomUser  # Asegúrate de que sea CustomUser

#/ Definición de la clase CustomUserAdmin que extiende de UserAdmin
# class CustomUserAdmin(UserAdmin):
#     add_form = UsuarioCreationForm
#     form = UsuarioChangeForm
#     model = CustomUser  # Asegúrate de que sea CustomUser
#     list_display = ['username', 'email', 'rol', 'departamento']

# Registro de la clase CustomUserAdmin en el sitio de administración de Django
# admin.site.register(CustomUser, CustomUserAdmin)  # Asegúrate de que sea CustomUser
