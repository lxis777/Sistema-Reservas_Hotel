from django.contrib import admin
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('ser_nombre', 'ser_precio_unitario', 'ser_activo')
    search_fields = ('ser_nombre',)
    list_filter = ('ser_activo',)
