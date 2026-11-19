from django.db import models
from reserva_core.models import Reserva
from servicio.models import Servicio

class ConsumoServicio(models.Model):
    con_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="consumos")
    con_servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="consumos")
    con_cantidad = models.PositiveIntegerField(default=1)
    con_fecha = models.DateField()
    con_observacion = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Consumo de servicio"
        verbose_name_plural = "Consumos de servicios"
        constraints = [
            models.UniqueConstraint(fields=["con_reserva", "con_servicio", "con_fecha"], name="consumo_reserva_servicio_fecha_unico")
        ]
        ordering = ["-con_fecha"]

    def __str__(self):
        return f"{self.con_servicio} x{self.con_cantidad} ({self.con_fecha})"
