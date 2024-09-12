from django.db import models
from datetime import date
from django.utils import timezone

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"

class Servicio(models.Model):
    nombre_servicio = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_servicio

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    id_partida_nacimiento = models.CharField(max_length=100, unique=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    estado_activo = models.BooleanField(default=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True)
    domicilio = models.TextField()
    diagnostico_medico = models.TextField()  # Campo para el diagnóstico médico
    servicios = models.ManyToManyField(Servicio, related_name='pacientes')  # Relación con los servicios
    medicamentos = models.TextField(blank=True, null=True)  # Nuevo campo para los medicamentos

    def calcular_edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def es_mayor_edad(self):
        return self.calcular_edad() >= 18

    def save(self, *args, **kwargs):
        # Verifica si los atributos 'edad' y 'menor_o_mayor' son realmente necesarios en el modelo
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Diagnostico(models.Model):
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, default='General')  # Adding a default value

    def __str__(self):
        return f'Diagnóstico {self.tipo}'

class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE, default=1)  # Asegúrate de que el ID 1 existe
    fecha_inicio = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f'Historia Clínica de {self.paciente.nombre}'

class Responsable(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='responsables')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.parentesco}'
