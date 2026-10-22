from django.contrib import admin
from .models import Huesped

@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ('hue_documento', 'hue_nombres', 'hue_apellidos', 'hue_correo', 'hue_telefono')
    search_fields = ('hue_documento', 'hue_nombres', 'hue_apellidos', 'hue_correo')
    list_filter = ('hue_fecha_registro',)
