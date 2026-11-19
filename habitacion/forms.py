from django import forms
from reservas_hotel.formularios import BootstrapMixin, FechaInput
from tipo_habitacion_core.models import TipoHabitacion
from .models import Habitacion


class HabitacionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ["hab_numero", "hab_piso", "fk_hab_tipo", "hab_estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fk_hab_tipo"].queryset = TipoHabitacion.objects.filter(tip_activo=True)


class DisponibilidadForm(BootstrapMixin, forms.Form):
    entrada = forms.DateField(label="Fecha de entrada", widget=FechaInput())
    salida = forms.DateField(label="Fecha de salida", widget=FechaInput())
    tipo = forms.ModelChoiceField(
        label="Tipo de habitación", required=False, empty_label="Todos los tipos",
        queryset=TipoHabitacion.objects.filter(tip_activo=True),
    )
    personas = forms.IntegerField(label="Personas", required=False, min_value=1)

    def clean(self):
        datos = super().clean()
        e, s = datos.get("entrada"), datos.get("salida")
        if e and s and s <= e:
            raise forms.ValidationError("La fecha de salida debe ser posterior a la de entrada.")
        return datos
