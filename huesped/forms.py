from django import forms
from reservas_hotel.formularios import BootstrapMixin
from .models import Huesped


class HuespedForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Huesped
        fields = ["hue_documento", "hue_nombres", "hue_apellidos", "hue_correo", "hue_telefono"]

    def clean_hue_documento(self):
        doc = self.cleaned_data["hue_documento"].strip()
        if not doc.replace("-", "").isalnum():
            raise forms.ValidationError("El documento solo puede tener letras, números y guiones.")
        return doc.upper()

    def clean_hue_telefono(self):
        tel = self.cleaned_data.get("hue_telefono", "").strip()
        if tel and not tel.replace(" ", "").replace("+", "").isdigit():
            raise forms.ValidationError("El teléfono solo puede contener números, espacios y '+'.")
        return tel
