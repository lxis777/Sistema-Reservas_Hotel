from django.contrib import admin
from .models import TipoHabitacion

@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ('tip_nombre', 'tip_capacidad', 'tip_precio_noche', 'tip_activo')
    search_fields = ('tip_nombre',)
    list_filter = ('tip_activo',)
