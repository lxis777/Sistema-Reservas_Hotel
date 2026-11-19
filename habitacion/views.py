from django.shortcuts import render
from django.urls import reverse_lazy

from reserva_core.models import Reserva
from reservas_hotel.vistas import CrearView, EditarView, EliminarView, ListaBuscableView
from tipo_habitacion_core.models import TipoHabitacion
from usuarios.permisos import ADMIN, HUESPED, PERSONAL, RECEPCION, rol_requerido
from .forms import DisponibilidadForm, HabitacionForm
from .models import Habitacion

URL_LISTA = reverse_lazy("habitaciones:lista")


class Lista(ListaBuscableView):
    roles_permitidos = PERSONAL
    queryset = Habitacion.objects.select_related("fk_hab_tipo")
    template_name = "habitacion/lista.html"
    campos_busqueda = ("hab_numero", "fk_hab_tipo__tip_nombre")
    filtros_exactos = ("hab_estado", "fk_hab_tipo")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["estados"] = Habitacion.ESTADOS
        ctx["tipos"] = TipoHabitacion.objects.all()
        return ctx


class Crear(CrearView):
    roles_permitidos = (ADMIN,)
    model, form_class, success_url = Habitacion, HabitacionForm, URL_LISTA
    titulo = "Nueva habitación"
    success_message = "Habitación %(hab_numero)s creada."


class Editar(EditarView):
    roles_permitidos = PERSONAL  # recepción puede cambiar el estado (p. ej. mantenimiento)
    model, form_class, success_url = Habitacion, HabitacionForm, URL_LISTA
    titulo = "Editar habitación"
    success_message = "Habitación %(hab_numero)s actualizada."


class Eliminar(EliminarView):
    roles_permitidos = (ADMIN,)
    model, success_url = Habitacion, URL_LISTA
    titulo = "Eliminar habitación"


@rol_requerido(ADMIN, RECEPCION, HUESPED)
def disponibilidad(request):
    """Consulta de habitaciones libres para un rango de fechas."""
    form = DisponibilidadForm(request.GET or None)
    libres = None
    if form.is_valid():
        e, s = form.cleaned_data["entrada"], form.cleaned_data["salida"]
        ocupadas = Reserva.objects.filter(
            res_estado__in=Reserva.ESTADOS_ACTIVOS, res_fecha_entrada__lt=s, res_fecha_salida__gt=e,
        ).values("fk_res_habitacion")
        libres = (Habitacion.objects.select_related("fk_hab_tipo")
                  .exclude(hab_estado="mantenimiento").exclude(pk__in=ocupadas)
                  .filter(fk_hab_tipo__tip_activo=True))
        if form.cleaned_data["tipo"]:
            libres = libres.filter(fk_hab_tipo=form.cleaned_data["tipo"])
        if form.cleaned_data["personas"]:
            libres = libres.filter(fk_hab_tipo__tip_capacidad__gte=form.cleaned_data["personas"])
        noches = (s - e).days
        libres = [(h, h.fk_hab_tipo.tip_precio_noche * noches) for h in libres]
        return render(request, "habitacion/disponibilidad.html",
                      {"form": form, "libres": libres, "noches": noches, "entrada": e, "salida": s})
    return render(request, "habitacion/disponibilidad.html", {"form": form, "libres": libres})
