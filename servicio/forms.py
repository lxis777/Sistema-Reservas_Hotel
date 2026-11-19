from django import forms
from reservas_hotel.formularios import BootstrapMixin
from .models import Servicio


class ServicioForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["ser_nombre", "ser_descripcion", "ser_precio_unitario", "ser_activo"]
        widgets = {"ser_descripcion": forms.Textarea(attrs={"rows": 3})}

    def clean_ser_precio_unitario(self):
        precio = self.cleaned_data["ser_precio_unitario"]
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio
