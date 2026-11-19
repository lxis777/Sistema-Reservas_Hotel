from django.db.models import Count
from django.urls import reverse_lazy
from django.views import generic

from reservas_hotel.vistas import CrearView, EditarView, EliminarView, ListaBuscableView
from usuarios.permisos import ADMIN, PERSONAL, RolRequeridoMixin
from .forms import HuespedForm
from .models import Huesped

URL_LISTA = reverse_lazy("huespedes:lista")


class Lista(ListaBuscableView):
    roles_permitidos = PERSONAL
    queryset = Huesped.objects.annotate(num_reservas=Count("reservas"))
    template_name = "huesped/lista.html"
    campos_busqueda = ("hue_documento", "hue_nombres", "hue_apellidos", "hue_correo")


class Detalle(RolRequeridoMixin, generic.DetailView):
    roles_permitidos = PERSONAL
    model = Huesped
    template_name = "huesped/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reservas"] = self.object.reservas.select_related("fk_res_habitacion__fk_hab_tipo").prefetch_related("consumos")
        return ctx


class Crear(CrearView):
    roles_permitidos = PERSONAL
    model, form_class, success_url = Huesped, HuespedForm, URL_LISTA
    titulo = "Registrar huésped"
    success_message = "Huésped %(hue_nombres)s %(hue_apellidos)s registrado."


class Editar(EditarView):
    roles_permitidos = PERSONAL
    model, form_class, success_url = Huesped, HuespedForm, URL_LISTA
    titulo = "Editar huésped"
    success_message = "Datos de %(hue_nombres)s %(hue_apellidos)s actualizados."


class Eliminar(EliminarView):
    roles_permitidos = (ADMIN,)
    model, success_url = Huesped, URL_LISTA
    titulo = "Eliminar huésped"
