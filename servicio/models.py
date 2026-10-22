from django.db import models

class Servicio(models.Model):
    ser_nombre = models.CharField(max_length=80, unique=True)
    ser_descripcion = models.TextField(blank=True)
    ser_precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    ser_activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ser_nombre"]

    def __str__(self):
        return f"{self.ser_nombre} (${self.ser_precio_unitario})"
