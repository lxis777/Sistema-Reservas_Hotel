from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_not_required
from django.db.models import Count, F, Sum
from django.shortcuts import render
from django.utils import timezone

from consumo_servicio.models import ConsumoServicio
from habitacion.models import Habitacion
from huesped.models import Huesped
from reserva_core.models import Reserva
from tipo_habitacion_core.models import TipoHabitacion
from usuarios.permisos import ADMIN, HUESPED, huesped_de, rol_de, rol_requerido


def _base_reservas():
    return Reserva.objects.select_related("fk_res_huesped", "fk_res_habitacion__fk_hab_tipo").prefetch_related("consumos")


@login_not_required
def inicio(request):
    rol = rol_de(request.user)
    if rol is None:
        if request.user.is_authenticated:
            return render(request, "panel/sin_rol.html")
        tipos = TipoHabitacion.objects.filter(tip_activo=True)
        return render(request, "panel/bienvenida.html", {"tipos": tipos})

    hoy = timezone.localdate()
    if rol == HUESPED:
        huesped = huesped_de(request.user)
        reservas = _base_reservas().filter(fk_res_huesped=huesped) if huesped else Reserva.objects.none()
        return render(request, "panel/inicio_huesped.html", {
            "huesped": huesped,
            "proxima": reservas.filter(res_estado__in=Reserva.ESTADOS_ACTIVOS, res_fecha_salida__gte=hoy)
                               .order_by("res_fecha_entrada").first(),
            "reservas": reservas[:5],
            "total_reservas": reservas.count(),
        })

    habitaciones = Habitacion.objects.all()
    total_hab = habitaciones.count()
    ocupadas = habitaciones.filter(hab_estado="ocupada").count()
    mantenimiento = habitaciones.filter(hab_estado="mantenimiento").count()
    operativas = total_hab - mantenimiento
    inicio_mes = hoy.replace(day=1)
    reservas_mes = _base_reservas().filter(res_fecha_entrada__gte=inicio_mes, res_fecha_entrada__lte=hoy,
                                           res_estado__in=["checkin", "finalizada", "confirmada"])
    ctx = {
        "hoy": hoy,
        "kpi_activas": Reserva.objects.filter(res_estado__in=Reserva.ESTADOS_ACTIVOS).count(),
        "kpi_en_casa": Reserva.objects.filter(res_estado="checkin").count(),
        "kpi_ocupacion": round(ocupadas * 100 / operativas) if operativas else 0,
        "kpi_huespedes": Huesped.objects.count(),
        "kpi_ingresos_mes": sum((r.valor_total for r in reservas_mes), Decimal("0")),
        "kpi_pendientes": Reserva.objects.filter(res_estado="pendiente").count(),
        "hab_total": total_hab, "hab_ocupadas": ocupadas, "hab_mantenimiento": mantenimiento,
        "hab_disponibles": total_hab - ocupadas - mantenimiento,
        "llegadas": _base_reservas().filter(res_estado__in=["pendiente", "confirmada"],
                                            res_fecha_entrada__range=(hoy, hoy + timedelta(days=7)))
                                    .order_by("res_fecha_entrada")[:6],
        "salidas": _base_reservas().filter(res_estado="checkin", res_fecha_salida__lte=hoy + timedelta(days=1))
                                   .order_by("res_fecha_salida")[:6],
        "habitaciones": habitaciones.select_related("fk_hab_tipo"),
    }
    return render(request, "panel/inicio.html", ctx)


@rol_requerido(ADMIN)
def reportes(request):
    hoy = timezone.localdate()
    desde = request.GET.get("desde") or hoy.replace(month=1, day=1).isoformat()
    hasta = request.GET.get("hasta") or (hoy + timedelta(days=60)).isoformat()
    reservas = _base_reservas().filter(res_fecha_entrada__range=(desde, hasta))
    facturables = [r for r in reservas if r.res_estado != "cancelada"]

    por_estado = []
    total = reservas.count() or 1
    etiquetas = dict(Reserva.ESTADOS)
    conteo = dict(reservas.values_list("res_estado").annotate(n=Count("pk")))
    for clave, nombre in Reserva.ESTADOS:
        n = conteo.get(clave, 0)
        por_estado.append({"clave": clave, "nombre": etiquetas[clave], "n": n, "pct": round(n * 100 / total)})

    por_tipo = {}
    for r in facturables:
        t = r.fk_res_habitacion.fk_hab_tipo.tip_nombre
        d = por_tipo.setdefault(t, {"tipo": t, "reservas": 0, "noches": 0, "alojamiento": Decimal("0")})
        d["reservas"] += 1
        d["noches"] += r.noches
        d["alojamiento"] += r.valor_alojamiento
    por_tipo = sorted(por_tipo.values(), key=lambda x: x["alojamiento"], reverse=True)
    max_tipo = max((x["alojamiento"] for x in por_tipo), default=1) or 1
    for x in por_tipo:
        x["pct"] = round(x["alojamiento"] * 100 / max_tipo)

    servicios = (ConsumoServicio.objects
                 .filter(fk_con_reserva__in=[r.pk for r in facturables])
                 .values("fk_con_servicio__ser_nombre")
                 .annotate(unidades=Sum("con_cantidad"), ingreso=Sum(F("con_cantidad") * F("con_valor_unitario")))
                 .order_by("-ingreso"))
    max_ser = max((s["ingreso"] for s in servicios), default=1) or 1
    servicios = [dict(s, pct=round(s["ingreso"] * 100 / max_ser)) for s in servicios]

    top_huespedes = {}
    for r in facturables:
        h = r.fk_res_huesped
        d = top_huespedes.setdefault(h.pk, {"huesped": h, "reservas": 0, "total": Decimal("0")})
        d["reservas"] += 1
        d["total"] += r.valor_total
    top_huespedes = sorted(top_huespedes.values(), key=lambda x: x["total"], reverse=True)[:5]

    return render(request, "panel/reportes.html", {
        "desde": desde, "hasta": hasta, "por_estado": por_estado, "por_tipo": por_tipo,
        "servicios": servicios, "top_huespedes": top_huespedes,
        "total_reservas": reservas.count(),
        "ingreso_alojamiento": sum((r.valor_alojamiento for r in facturables), Decimal("0")),
        "ingreso_servicios": sum((r.valor_consumos for r in facturables), Decimal("0")),
    })


def error_403(request, exception=None):
    return render(request, "403.html", status=403)


@login_not_required
def error_404(request, exception=None):
    return render(request, "404.html", status=404)
