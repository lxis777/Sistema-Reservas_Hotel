from django.contrib import admin
from .models import Reserva
from consumo_servicio.models import ConsumoServicio

class ConsumoServicioInline(admin.TabularInline):
    model = ConsumoServicio
    extra = 1

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("res_codigo", "res_huesped", "res_habitacion", "res_fecha_entrada", "res_fecha_salida", "res_estado")
    search_fields = ("res_codigo", "res_huesped__hue_nombres", "res_huesped__hue_apellidos", "res_habitacion__hab_numero")
    list_filter = ("res_estado", "res_fecha_entrada", "res_fecha_salida")
    inlines = [ConsumoServicioInline]
