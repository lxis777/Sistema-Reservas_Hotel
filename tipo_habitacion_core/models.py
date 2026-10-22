from django.db import models

class TipoHabitacion(models.Model):
    tip_nombre = models.CharField(max_length=80, unique=True)
    tip_descripcion = models.TextField(blank=True)
    tip_capacidad = models.PositiveSmallIntegerField(default=2)
    tip_precio_noche = models.DecimalField(max_digits=10, decimal_places=2)
    tip_activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de habitación"
        verbose_name_plural = "Tipos de habitación"
        ordering = ["tip_nombre"]

    def __str__(self):
        return f"{self.tip_nombre} (${self.tip_precio_noche}/noche)"
