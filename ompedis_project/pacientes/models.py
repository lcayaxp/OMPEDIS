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
    nombre = models.CharField(max_length=100)  # Nombre del paciente
    apellido = models.CharField(max_length=100)  # Apellido del paciente
    id_partida_nacimiento = models.CharField(max_length=100, unique=True)  # Identificación única del paciente
    fecha_nacimiento = models.DateField()  # Fecha de nacimiento del paciente
    genero = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])  # Género del paciente
    estado_activo = models.BooleanField(default=True)  # Indica si el paciente está activo o no
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)  # Relación con el departamento
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True)  # Relación con el municipio
    domicilio = models.TextField()  # Dirección del domicilio del paciente
    diagnostico_medico = models.TextField()  # Campo para el diagnóstico médico del paciente
    servicios = models.ManyToManyField(Servicio, related_name='pacientes')  # Relación con los servicios que recibe el paciente
    medicamentos = models.TextField(blank=True, null=True)  # Campo para registrar los medicamentos (opcional)

    def calcular_edad(self):
        # Método para calcular la edad del paciente
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def es_mayor_edad(self):
        # Método para determinar si el paciente es mayor de edad
        return self.calcular_edad() >= 18

    def save(self, *args, **kwargs):
        # Método personalizado de guardado, en este caso no se añade lógica adicional, solo se llama al método padre
        super().save(*args, **kwargs)

    def __str__(self):
        # Devuelve el nombre completo del paciente como representación de la instancia
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

# Modelo para representar un responsable (familiar o tutor) de un paciente
class Responsable(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='responsables')  # Relación con el paciente
    nombre = models.CharField(max_length=100)  # Nombre del responsable
    apellido = models.CharField(max_length=100)  # Apellido del responsable
    parentesco = models.CharField(max_length=50)  # Relación con el paciente (por ejemplo, madre, padre, tutor)
    telefono = models.CharField(max_length=20)  # Teléfono de contacto del responsable

    def __str__(self):
        # Devuelve el nombre completo del responsable junto con su parentesco con el paciente
        return f'{self.nombre} {self.apellido} - {self.parentesco}'
