from django.contrib.auth.models import AbstractUser
from django.db import models

# Definición de roles
ROLES_CHOICES = [
    ('administrador', 'Administrador'),
    ('moderador', 'Moderador'),
    ('usuario', 'Usuario'),
]

class CustomUser(AbstractUser):
    rol = models.CharField(max_length=20, choices=ROLES_CHOICES, default='moderador')
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return self.username
