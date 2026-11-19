"""Carga datos de prueba: python manage.py cargar_datos  (usar --reiniciar para borrar los existentes)."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from consumo_servicio.models import ConsumoServicio
from habitacion.models import Habitacion
from huesped.models import Huesped
from reserva_core.models import Reserva
from servicio.models import Servicio
from tipo_habitacion_core.models import TipoHabitacion
from usuarios.models import Perfil


class Command(BaseCommand):
    help = "Carga datos de prueba del hotel y crea los usuarios de cada rol."

    def add_arguments(self, parser):
        parser.add_argument("--reiniciar", action="store_true", help="Elimina los datos antes de cargar.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["reiniciar"]:
            ConsumoServicio.objects.all().delete()
            Reserva.objects.all().delete()
            Perfil.objects.all().delete()
            User.objects.all().delete()
            Huesped.objects.all().delete()
            Habitacion.objects.all().delete()
            TipoHabitacion.objects.all().delete()
            Servicio.objects.all().delete()

        hoy = timezone.localdate()
        D = lambda n: hoy + timedelta(days=n)

        # ---------- Tipos de habitación ----------
        tipos = {}
        for nombre, desc, cap, precio in [
            ("Sencilla", "Cama semidoble, baño privado, aire acondicionado y wifi.", 1, 140000),
            ("Doble", "Dos camas dobles, aire acondicionado, TV y minibar.", 2, 210000),
            ("Familiar Wayuu", "Amplia, decorada con mochilas y chinchorros wayuu. Ideal para familias.", 5, 340000),
            ("Suite Vista al Mar", "Cama king, balcón con vista al mar Caribe y jacuzzi.", 2, 480000),
        ]:
            tipos[nombre], _ = TipoHabitacion.objects.get_or_create(
                tip_nombre=nombre, defaults=dict(tip_descripcion=desc, tip_capacidad=cap, tip_precio_noche=Decimal(precio)))

        # ---------- Habitaciones ----------
        habs = {}
        plan = [("101", 1, "Sencilla"), ("102", 1, "Sencilla"), ("103", 1, "Doble"), ("104", 1, "Doble"),
                ("201", 2, "Doble"), ("202", 2, "Doble"), ("203", 2, "Familiar Wayuu"), ("204", 2, "Familiar Wayuu"),
                ("301", 3, "Suite Vista al Mar"), ("302", 3, "Suite Vista al Mar"), ("303", 3, "Doble"), ("304", 3, "Sencilla")]
        for num, piso, tipo in plan:
            habs[num], _ = Habitacion.objects.get_or_create(hab_numero=num, defaults=dict(hab_piso=piso, fk_hab_tipo=tipos[tipo]))
        Habitacion.objects.filter(hab_numero="304").update(hab_estado="mantenimiento")

        # ---------- Servicios ----------
        servs = {}
        for nombre, desc, precio in [
            ("Desayuno buffet", "Desayuno típico costeño: arepa de huevo, frutas y jugos.", 28000),
            ("Lavandería", "Lavado y planchado por prenda.", 9000),
            ("Minibar", "Consumo de bebidas y snacks del minibar.", 15000),
            ("Spa y masajes", "Masaje relajante de 60 minutos.", 120000),
            ("Tour Cabo de la Vela", "Excursión de día completo en 4x4 con almuerzo.", 190000),
            ("Traslado aeropuerto", "Traslado Aeropuerto Almirante Padilla ↔ hotel.", 35000),
            ("Cena a la carta", "Cena en el restaurante con friche o pescado del día.", 65000),
            ("Parqueadero", "Parqueadero cubierto por noche.", 12000),
        ]:
            servs[nombre], _ = Servicio.objects.get_or_create(ser_nombre=nombre, defaults=dict(ser_descripcion=desc, ser_precio_unitario=Decimal(precio)))
        Servicio.objects.filter(ser_nombre="Parqueadero").update(ser_activo=False)

        # ---------- Huéspedes ----------
        hues = {}
        for doc, nom, ape, correo, tel in [
            ("1118801234", "Yeison", "Pushaina Epiayú", "yeison.pushaina@correo.com", "3004561234"),
            ("40934567", "María José", "Iguarán Brito", "mariajose.iguaran@correo.com", "3015558899"),
            ("1124012345", "Andrés", "Mendoza Cotes", "andres.mendoza@correo.com", "3127774455"),
            ("52987654", "Laura", "Gómez Restrepo", "laura.gomez@correo.com", "3159991122"),
            ("1065432109", "Carlos", "Uriana Ipuana", "carlos.uriana@correo.com", "3201112233"),
            ("1002345678", "Valentina", "Ospina Díaz", "valentina.ospina@correo.com", "3186667788"),
            ("17654321", "Jorge", "Barros Fuentes", "jorge.barros@correo.com", "3043332211"),
            ("1120567890", "Daniela", "Solano Pimienta", "daniela.solano@correo.com", "3112224466"),
            ("PA98765", "John", "Smith", "john.smith@mail.com", "+1 305 555 0101"),
            ("1047890123", "Sofía", "Arregocés Daza", "sofia.arregoces@correo.com", "3168889900"),
        ]:
            hues[doc], _ = Huesped.objects.get_or_create(hue_documento=doc, defaults=dict(
                hue_nombres=nom, hue_apellidos=ape, hue_correo=correo, hue_telefono=tel))

        # ---------- Usuarios por rol ----------
        def usuario(username, clave, nombre, apellido, rol, huesped=None, superuser=False):
            u = User.objects.filter(username=username).first()
            if not u:
                crear = User.objects.create_superuser if superuser else User.objects.create_user
                u = crear(username=username, password=clave, email=f"{username}@brisasguajira.co",
                          first_name=nombre, last_name=apellido)
                if not superuser and rol != Perfil.ROL_HUESPED:
                    u.is_staff = False
                    u.save()
            Perfil.objects.update_or_create(fk_per_usuario=u, defaults={"per_rol": rol, "fk_per_huesped": huesped})

        usuario("admin", "Admin12345", "Administrador", "General", Perfil.ROL_ADMINISTRADOR, superuser=True)
        usuario("recepcion", "Recepcion123", "Katherine", "Fince", Perfil.ROL_RECEPCIONISTA)
        usuario("huesped", "Huesped123", "Yeison", "Pushaina Epiayú", Perfil.ROL_HUESPED, huesped=hues["1118801234"])

        if Reserva.objects.exists():
            self.stdout.write(self.style.WARNING("Ya existen reservas; no se crearon nuevas (use --reiniciar)."))
            return

        # ---------- Reservas con sus consumos ----------
        # (huésped, habitación, entrada, salida, estado, [(servicio, cantidad, día relativo a la entrada)])
        reservas = [
            ("1118801234", "301", -40, -36, "finalizada", [("Desayuno buffet", 8, 1), ("Tour Cabo de la Vela", 2, 2), ("Spa y masajes", 1, 3)]),
            ("40934567", "203", -25, -20, "finalizada", [("Desayuno buffet", 15, 1), ("Traslado aeropuerto", 2, 0), ("Cena a la carta", 4, 2)]),
            ("1124012345", "103", -18, -16, "finalizada", [("Lavandería", 6, 1), ("Minibar", 3, 1)]),
            ("52987654", "302", -12, -9, "finalizada", [("Spa y masajes", 2, 1), ("Cena a la carta", 2, 2), ("Desayuno buffet", 6, 1)]),
            ("1065432109", "101", -8, -6, "cancelada", []),
            ("1002345678", "201", -3, 2, "checkin", [("Desayuno buffet", 6, 1), ("Minibar", 2, 2)]),
            ("17654321", "302", -2, 1, "checkin", [("Traslado aeropuerto", 1, 0), ("Tour Cabo de la Vela", 2, 1)]),
            ("1120567890", "104", -1, 3, "checkin", [("Lavandería", 4, 0)]),
            ("PA98765", "204", -1, 0, "checkin", [("Cena a la carta", 3, 0)]),
            ("1047890123", "102", 0, 2, "confirmada", []),
            ("1118801234", "301", 3, 6, "confirmada", [("Traslado aeropuerto", 1, 0)]),
            ("40934567", "202", 2, 5, "pendiente", []),
            ("1124012345", "203", 5, 9, "confirmada", []),
            ("52987654", "303", 6, 8, "pendiente", []),
            ("1065432109", "101", 10, 12, "pendiente", []),
            ("1118801234", "102", 14, 17, "pendiente", []),
            ("17654321", "201", 20, 23, "confirmada", []),
            ("1002345678", "301", 25, 28, "pendiente", []),
        ]
        for i, (doc, hab, ent, sal, estado, consumos) in enumerate(reservas, start=1):
            r = Reserva(
                res_codigo=f"RES-{D(ent):%Y%m}-{i:04d}", fk_res_huesped=hues[doc], fk_res_habitacion=habs[hab],
                res_fecha_reserva=D(min(ent, 0) - 7), res_fecha_entrada=D(ent), res_fecha_salida=D(sal),
                res_estado=estado,
                res_observaciones="Solicita habitación en piso alto." if i % 5 == 0 else "",
            )
            r.save()
            for ser, cant, dia in consumos:
                ConsumoServicio.objects.create(fk_con_reserva=r, fk_con_servicio=servs[ser], con_cantidad=cant,
                                               con_fecha=D(ent + dia))

        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados: {TipoHabitacion.objects.count()} tipos, {Habitacion.objects.count()} habitaciones, "
            f"{Huesped.objects.count()} huéspedes, {Servicio.objects.count()} servicios, "
            f"{Reserva.objects.count()} reservas, {ConsumoServicio.objects.count()} consumos."))
