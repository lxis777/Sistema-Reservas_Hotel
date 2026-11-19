from django.db.models import Count, Sum
from django.urls import reverse_lazy

from reservas_hotel.vistas import CrearView, EditarView, EliminarView, ListaBuscableView
from usuarios.permisos import ADMIN, PERSONAL
from .forms import ServicioForm
from .models import Servicio

URL_LISTA = reverse_lazy("servicios:lista")


class Lista(ListaBuscableView):
    roles_permitidos = PERSONAL
    queryset = Servicio.objects.annotate(veces=Count("consumos"), unidades=Sum("consumos__con_cantidad"))
    template_name = "servicio/lista.html"
    campos_busqueda = ("ser_nombre", "ser_descripcion")
    filtros_exactos = ("ser_activo",)


class Crear(CrearView):
    roles_permitidos = (ADMIN,)
    model, form_class, success_url = Servicio, ServicioForm, URL_LISTA
    titulo = "Nuevo servicio"
    success_message = "Servicio «%(ser_nombre)s» creado."


class Editar(EditarView):
    roles_permitidos = (ADMIN,)
    model, form_class, success_url = Servicio, ServicioForm, URL_LISTA
    titulo = "Editar servicio"
    success_message = "Servicio «%(ser_nombre)s» actualizado."


class Eliminar(EliminarView):
    roles_permitidos = (ADMIN,)
    model, success_url = Servicio, URL_LISTA
    titulo = "Eliminar servicio"
