from django.db import models
from datetime import date
from django.utils import timezone

# Modelo para representar un departamento (entidad administrativa)
class Departamento(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del departamento

    def __str__(self):
        return self.nombre  # Devuelve el nombre del departamento como representación de la instancia

# Modelo para representar un municipio, relacionado con un departamento
class Municipio(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del municipio
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)  # Relación con el departamento

    def __str__(self):
        # Devuelve el nombre del municipio junto con el nombre del departamento al que pertenece
        return f"{self.nombre}, {self.departamento.nombre}"

# Modelo para representar los servicios que se pueden prestar a los pacientes
class Servicio(models.Model):
    nombre_servicio = models.CharField(max_length=100)  # Nombre del servicio prestado

    def __str__(self):
        return self.nombre_servicio  # Devuelve el nombre del servicio como representación de la instancia

# Modelo para representar un paciente
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
    diagnostico_medico = models.TextField()
    servicios = models.ManyToManyField(Servicio, related_name='pacientes')
    medicamentos = models.TextField(blank=True, null=True)
    
    # Campos de Responsable
    responsable_nombre = models.CharField(max_length=100)
    responsable_apellido = models.CharField(max_length=100)
    responsable_parentesco = models.CharField(max_length=50)
    responsable_telefono = models.CharField(max_length=20)

    def calcular_edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def es_mayor_edad(self):
        return self.calcular_edad() >= 18

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo para representar un diagnóstico
class Diagnostico(models.Model):
    descripcion = models.TextField(blank=True, null=True)  # Descripción del diagnóstico (opcional)
    tipo = models.CharField(max_length=50, default='General')  # Tipo de diagnóstico (por ejemplo, general, específico)

    def __str__(self):
        # Devuelve el tipo de diagnóstico como representación de la instancia
        return f'Diagnóstico {self.tipo}'

# Modelo para representar la historia clínica de un paciente
class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)  # Relación con el paciente
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE, default=1)  # Relación con el diagnóstico, asegurarse que el ID 1 exista
    fecha_inicio = models.DateField(default=timezone.now)  # Fecha en la que se inicia la historia clínica
    estado = models.CharField(max_length=50, default='Pendiente')  # Estado actual de la historia clínica (por ejemplo, pendiente, cerrado)

    def __str__(self):
        # Devuelve una representación indicando a quién pertenece la historia clínica
        return f'Historia Clínica de {self.paciente.nombre}'

# Elimina esta clase
# class Responsable(models.Model):
#     paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='responsables')
#     nombre = models.CharField(max_length=100)
#     apellido = models.CharField(max_length=100)
#     parentesco = models.CharField(max_length=50)
#     telefono = models.CharField(max_length=20)

#     def __str__(self):
#         return f'{self.nombre} {self.apellido} - {self.parentesco}'