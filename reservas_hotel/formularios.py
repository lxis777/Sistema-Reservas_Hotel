"""Utilidades compartidas para que todos los formularios usen las clases de Bootstrap."""
from django import forms


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", "form-check-input")
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                w.attrs.setdefault("class", "form-select")
            else:
                w.attrs.setdefault("class", "form-control")

    def full_clean(self):
        super().full_clean()
        # Marca en rojo (is-invalid) los campos que tienen errores
        for nombre in self.errors:
            if nombre in self.fields:
                w = self.fields[nombre].widget
                w.attrs["class"] = (w.attrs.get("class", "") + " is-invalid").strip()


class FechaInput(forms.DateInput):
    input_type = "date"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, format="%Y-%m-%d")
