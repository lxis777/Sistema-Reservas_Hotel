from django.db import models
from tipo_habitacion_core.models import TipoHabitacion

class Habitacion(models.Model):
    hab_numero = models.CharField(max_length=10, unique=True)
    hab_piso = models.PositiveSmallIntegerField(default=1)
    hab_estado = models.CharField(max_length=20, choices=[
        ("disponible", "Disponible"), ("ocupada", "Ocupada"),
        ("mantenimiento", "Mantenimiento")
    ], default="disponible")
    hab_tipo = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name="habitaciones")

    class Meta:
        ordering = ["hab_numero"]

    def __str__(self):
        return f"Habitación {self.hab_numero}"
