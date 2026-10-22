from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from huesped.models import Huesped
from habitacion.models import Habitacion

class Reserva(models.Model):
    res_codigo = models.CharField(max_length=20, unique=True)
    res_huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, related_name="reservas")
    res_habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name="reservas")
    res_fecha_reserva = models.DateField(default=timezone.localdate)
    res_fecha_entrada = models.DateField()
    res_fecha_salida = models.DateField()
    res_estado = models.CharField(max_length=20, choices=[
        ("pendiente", "Pendiente"), ("confirmada", "Confirmada"),
        ("checkin", "En estadía"), ("finalizada", "Finalizada"),
        ("cancelada", "Cancelada")
    ], default="pendiente")
    res_observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["-res_fecha_entrada"]

    def clean(self):
        if self.res_fecha_salida and self.res_fecha_entrada and self.res_fecha_salida <= self.res_fecha_entrada:
            raise ValidationError("La fecha de salida debe ser posterior a la fecha de entrada.")

    def __str__(self):
        return f"{self.res_codigo} - {self.res_huesped}"
