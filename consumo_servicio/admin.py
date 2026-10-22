from django.contrib import admin
from .models import ConsumoServicio

@admin.register(ConsumoServicio)
class ConsumoServicioAdmin(admin.ModelAdmin):
    list_display = ("con_reserva", "con_servicio", "con_cantidad", "con_fecha")
    search_fields = ("con_reserva__res_codigo", "con_servicio__ser_nombre")
    list_filter = ("con_fecha", "con_servicio")
