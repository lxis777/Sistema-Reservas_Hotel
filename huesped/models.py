from django.db import models

class Huesped(models.Model):
    hue_documento = models.CharField(max_length=30, unique=True)
    hue_nombres = models.CharField(max_length=100)
    hue_apellidos = models.CharField(max_length=100)
    hue_correo = models.EmailField(blank=True)
    hue_telefono = models.CharField(max_length=25, blank=True)
    hue_fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["hue_apellidos", "hue_nombres"]

    def __str__(self):
        return f"{self.hue_nombres} {self.hue_apellidos} ({self.hue_documento})"
