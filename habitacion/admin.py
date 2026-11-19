from django.contrib import admin
from .models import Habitacion

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('hab_numero', 'hab_tipo', 'hab_piso', 'hab_estado')
    search_fields = ('hab_numero',)
    list_filter = ('hab_estado', 'hab_piso')
