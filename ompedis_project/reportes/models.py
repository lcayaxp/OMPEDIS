from django.db import models
from pacientes.models import Paciente
from datetime import date

class Reporte(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='reportes/', blank=True, null=True)

    def __str__(self):
        return f'Reporte de {self.paciente.nombre} el {self.fecha}'

class SesionTerapia(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, default='Masculino')
    diagnostico = models.CharField(max_length=255)
    area = models.CharField(max_length=255, choices=[
        ('Neurología', 'Neurología'), 
        ('Traumatología', 'Traumatología')
    ])
    fecha_sesion = models.DateField()

    def calcular_edad(self):
        today = date.today()
        return today.year - self.paciente.fecha_nacimiento.year - ((today.month, today.day) < (self.paciente.fecha_nacimiento.month, self.paciente.fecha_nacimiento.day))

    def __str__(self):
        return f"{self.paciente} - {self.fecha_sesion}"
