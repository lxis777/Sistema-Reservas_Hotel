from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from consumo_servicio.models import ConsumoServicio
from habitacion.models import Habitacion
from huesped.models import Huesped
from reservas_hotel.formularios import BootstrapMixin, FechaInput
from servicio.models import Servicio
from .models import Reserva


class ReservaForm(BootstrapMixin, forms.ModelForm):
    """Formulario del personal (administrador / recepcionista)."""

    class Meta:
        model = Reserva
        fields = ["fk_res_huesped", "fk_res_habitacion", "res_fecha_entrada",
                  "res_fecha_salida", "res_estado", "res_observaciones"]
        widgets = {
            "res_fecha_entrada": FechaInput(),
            "res_fecha_salida": FechaInput(),
            "res_observaciones": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fk_res_huesped"].queryset = Huesped.objects.all()
        self.fields["fk_res_habitacion"].queryset = (
            Habitacion.objects.select_related("fk_hab_tipo").exclude(hab_estado="mantenimiento")
            | Habitacion.objects.filter(pk=self.instance.fk_res_habitacion_id or 0)
        ).distinct()
        if not self.instance.pk:
            self.fields["res_estado"].choices = [c for c in Reserva.ESTADOS if c[0] in ("pendiente", "confirmada", "checkin")]

    def clean_res_fecha_entrada(self):
        fecha = self.cleaned_data["res_fecha_entrada"]
        if not self.instance.pk and fecha < timezone.localdate():
            raise forms.ValidationError("No se pueden crear reservas con fecha de entrada en el pasado.")
        return fecha


class SolicitudReservaForm(BootstrapMixin, forms.ModelForm):
    """Formulario reducido para que el huésped solicite su propia reserva."""

    class Meta:
        model = Reserva
        fields = ["fk_res_habitacion", "res_fecha_entrada", "res_fecha_salida", "res_observaciones"]
        widgets = {
            "res_fecha_entrada": FechaInput(),
            "res_fecha_salida": FechaInput(),
            "res_observaciones": forms.Textarea(attrs={"rows": 2, "placeholder": "Peticiones especiales (opcional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fk_res_habitacion"].queryset = (
            Habitacion.objects.select_related("fk_hab_tipo")
            .filter(fk_hab_tipo__tip_activo=True).exclude(hab_estado="mantenimiento")
        )

    def clean_res_fecha_entrada(self):
        fecha = self.cleaned_data["res_fecha_entrada"]
        if fecha < timezone.localdate():
            raise forms.ValidationError("La fecha de entrada no puede estar en el pasado.")
        return fecha


class ConsumoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ConsumoServicio
        fields = ["fk_con_servicio", "con_cantidad", "con_fecha", "con_observacion"]
        widgets = {"con_fecha": FechaInput(), "con_observacion": forms.TextInput(attrs={"placeholder": "Opcional"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fk_con_servicio"].queryset = Servicio.objects.filter(ser_activo=True) | Servicio.objects.filter(
            pk=self.instance.fk_con_servicio_id or 0)
        self.fields["con_cantidad"].widget.attrs["min"] = 1

    def clean(self):
        datos = super().clean()
        if "fk_con_servicio" in self.changed_data:
            self.instance.con_valor_unitario = None  # se recalcula con el precio del nuevo servicio
        return datos

    def clean_con_cantidad(self):
        cant = self.cleaned_data["con_cantidad"]
        if cant < 1:
            raise forms.ValidationError("Mínimo 1.")
        return cant


class ConsumoFormSetBase(forms.BaseInlineFormSet):
    def clean(self):
        vistos = set()
        reserva = self.instance
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            servicio, fecha = form.cleaned_data.get("fk_con_servicio"), form.cleaned_data.get("con_fecha")
            clave = (servicio, fecha)
            if clave in vistos:
                raise forms.ValidationError(
                    f"El servicio «{servicio.ser_nombre}» está repetido para el {fecha:%d/%m/%Y}; súmalo en una sola fila.")
            vistos.add(clave)
            if fecha and reserva.res_fecha_entrada and reserva.res_fecha_salida and not (
                    reserva.res_fecha_entrada <= fecha <= reserva.res_fecha_salida):
                form.add_error("con_fecha", "Debe estar dentro de la estadía.")
        super().clean()


ConsumoFormSet = inlineformset_factory(
    Reserva, ConsumoServicio, form=ConsumoForm, formset=ConsumoFormSetBase,
    extra=0, can_delete=True,
)


class FiltroReservaForm(BootstrapMixin, forms.Form):
    q = forms.CharField(label="Buscar", required=False,
                        widget=forms.TextInput(attrs={"placeholder": "Código, huésped, documento o habitación"}))
    estado = forms.ChoiceField(label="Estado", required=False, choices=[("", "Todos los estados")] + Reserva.ESTADOS)
    desde = forms.DateField(label="Entrada desde", required=False, widget=FechaInput())
    hasta = forms.DateField(label="Entrada hasta", required=False, widget=FechaInput())
