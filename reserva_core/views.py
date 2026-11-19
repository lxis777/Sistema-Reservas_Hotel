from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from usuarios.permisos import ADMIN, HUESPED, PERSONAL, RECEPCION, huesped_de, rol_de, rol_requerido
from habitacion.models import Habitacion
from servicio.models import Servicio
from .forms import ConsumoFormSet, FiltroReservaForm, ReservaForm, SolicitudReservaForm
from .models import Reserva


def _reservas_visibles(user):
    """El personal ve todas las reservas; el huésped solo las suyas."""
    qs = Reserva.objects.select_related("fk_res_huesped", "fk_res_habitacion__fk_hab_tipo").prefetch_related(
        "consumos__fk_con_servicio")
    if rol_de(user) == HUESPED:
        return qs.filter(fk_res_huesped=huesped_de(user))
    return qs


def _obtener_reserva(request, pk):
    return get_object_or_404(_reservas_visibles(request.user), pk=pk)


# ------------------------------------------------------------------ LISTAR
@rol_requerido(ADMIN, RECEPCION, HUESPED)
def lista(request):
    filtro = FiltroReservaForm(request.GET or None)
    reservas = _reservas_visibles(request.user)
    if filtro.is_valid():
        q = filtro.cleaned_data["q"]
        if q:
            reservas = reservas.filter(
                Q(res_codigo__icontains=q) | Q(fk_res_huesped__hue_nombres__icontains=q)
                | Q(fk_res_huesped__hue_apellidos__icontains=q) | Q(fk_res_huesped__hue_documento__icontains=q)
                | Q(fk_res_habitacion__hab_numero__icontains=q)
            )
        if filtro.cleaned_data["estado"]:
            reservas = reservas.filter(res_estado=filtro.cleaned_data["estado"])
        if filtro.cleaned_data["desde"]:
            reservas = reservas.filter(res_fecha_entrada__gte=filtro.cleaned_data["desde"])
        if filtro.cleaned_data["hasta"]:
            reservas = reservas.filter(res_fecha_entrada__lte=filtro.cleaned_data["hasta"])

    pagina = Paginator(reservas, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "reserva_core/lista.html", {
        "pagina": pagina, "filtro": filtro, "total": reservas.count(), "params": params.urlencode(),
    })


# ------------------------------------------------------------------ DETALLE
@rol_requerido(ADMIN, RECEPCION, HUESPED)
def detalle(request, pk):
    reserva = _obtener_reserva(request, pk)
    return render(request, "reserva_core/detalle.html", {"reserva": reserva})


# ------------------------------------------------------------------ CREAR / EDITAR
def _guardar_reserva(request, reserva=None):
    es_nueva = reserva is None
    reserva = reserva or Reserva()
    inicial = {}
    if es_nueva:  # permite llegar desde "Disponibilidad" con datos precargados
        inicial = {k: request.GET[k] for k in ("fk_res_habitacion", "res_fecha_entrada", "res_fecha_salida", "fk_res_huesped")
                   if request.GET.get(k)}
    form = ReservaForm(request.POST or None, instance=reserva, initial=inicial)
    formset = ConsumoFormSet(request.POST or None, instance=reserva, prefix="consumos")

    if request.method == "POST":
        form_ok = form.is_valid()
        if form_ok:
            formset.instance = form.instance  # para validar fechas de consumo contra la estadía
        if form_ok and formset.is_valid():
            with transaction.atomic():
                reserva = form.save()
                formset.instance = reserva
                formset.save()
            accion = "registrada" if es_nueva else "actualizada"
            messages.success(request, f"Reserva {reserva.res_codigo} {accion} correctamente.")
            return redirect("reservas:detalle", pk=reserva.pk)
        messages.error(request, "Revisa los campos marcados en rojo.")

    return render(request, "reserva_core/formulario.html", {
        "form": form, "formset": formset, "reserva": reserva if not es_nueva else None,
        "precios_habitacion": {h.pk: float(h.fk_hab_tipo.tip_precio_noche)
                               for h in Habitacion.objects.select_related("fk_hab_tipo")},
        "precios_servicio": {s.pk: float(s.ser_precio_unitario) for s in Servicio.objects.all()},
    })


@rol_requerido(ADMIN, RECEPCION)
def crear(request):
    return _guardar_reserva(request)


@rol_requerido(ADMIN, RECEPCION)
def editar(request, pk):
    reserva = _obtener_reserva(request, pk)
    if not reserva.puede_editarse and rol_de(request.user) != ADMIN:
        messages.warning(request, "Las reservas finalizadas o canceladas solo las puede editar el administrador.")
        return redirect("reservas:detalle", pk=pk)
    return _guardar_reserva(request, reserva)


# ------------------------------------------------------------------ ELIMINAR
@rol_requerido(ADMIN, RECEPCION)
def eliminar(request, pk):
    reserva = _obtener_reserva(request, pk)
    if request.method == "POST":
        codigo = reserva.res_codigo
        try:
            reserva.delete()  # los consumos se eliminan en cascada (entidad débil)
        except ProtectedError:
            messages.error(request, "No se pudo eliminar la reserva porque tiene registros protegidos.")
            return redirect("reservas:detalle", pk=pk)
        messages.success(request, f"Reserva {codigo} eliminada junto con sus consumos.")
        return redirect("reservas:lista")
    return render(request, "reserva_core/confirmar_eliminar.html", {"reserva": reserva})


# ------------------------------------------------------------------ CAMBIOS DE ESTADO
TRANSICIONES = {
    # accion: (estados de origen permitidos, nuevo estado, roles, mensaje)
    "confirmar": (("pendiente",), "confirmada", PERSONAL, "confirmada"),
    "checkin": (("pendiente", "confirmada"), "checkin", PERSONAL, "con check-in registrado"),
    "checkout": (("checkin",), "finalizada", PERSONAL, "finalizada (check-out)"),
    "cancelar": (("pendiente", "confirmada"), "cancelada", PERSONAL + (HUESPED,), "cancelada"),
}


@require_POST
@rol_requerido(ADMIN, RECEPCION, HUESPED)
def cambiar_estado(request, pk, accion):
    reserva = _obtener_reserva(request, pk)
    if accion not in TRANSICIONES:
        raise PermissionDenied
    origenes, nuevo, roles, texto = TRANSICIONES[accion]
    rol = rol_de(request.user)
    if rol not in roles or (rol == HUESPED and reserva.res_estado != "pendiente"):
        messages.error(request, "No puedes realizar esa acción sobre esta reserva.")
    elif reserva.res_estado not in origenes:
        messages.warning(request, f"La reserva está «{reserva.get_res_estado_display()}» y no admite esa acción.")
    else:
        reserva.res_estado = nuevo
        reserva.save()
        messages.success(request, f"Reserva {reserva.res_codigo} {texto}.")
    siguiente = request.POST.get("next")
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return redirect(siguiente)
    return redirect("reservas:detalle", pk=pk)


# ------------------------------------------------------------------ HUÉSPED: SOLICITAR
@rol_requerido(HUESPED)
def solicitar(request):
    huesped = huesped_de(request.user)
    if huesped is None:
        messages.error(request, "Tu usuario no tiene un huésped asociado. Comunícate con recepción.")
        return redirect("panel:inicio")
    inicial = {k: request.GET.get(k) for k in ("fk_res_habitacion", "res_fecha_entrada", "res_fecha_salida") if request.GET.get(k)}
    form = SolicitudReservaForm(request.POST or None, initial=inicial,
                                instance=Reserva(fk_res_huesped=huesped, res_estado="pendiente"))
    if request.method == "POST":
        if form.is_valid():
            reserva = form.save()
            messages.success(request, f"¡Solicitud enviada! Tu código es {reserva.res_codigo}. Recepción la confirmará pronto.")
            return redirect("reservas:detalle", pk=reserva.pk)
        messages.error(request, "Revisa los datos de la solicitud.")
    return render(request, "reserva_core/solicitar.html", {"form": form})
