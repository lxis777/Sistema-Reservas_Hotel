# Guía para la socialización (≈ 10–12 minutos)

Repartan las partes entre los integrantes; todos deben poder responder sobre cualquiera.

## 1. Estructura del proyecto (1–2 min)
- Mostrar las apps: `reserva_core` (proceso principal), `huesped`, `habitacion`, `tipo_habitacion_core`, `servicio`, `consumo_servicio`, `usuarios` (login y roles) y `panel` (tablero y reportes).
- Carpeta `templates/`: `base.html` (navbar, aside, mensajes, footer) y una carpeta por app; las demás páginas usan `{% extends "base.html" %}`.
- Cada app tiene `urls.py` con `app_name`; los enlaces se arman con `{% url 'reservas:detalle' r.pk %}`.
- Bootstrap 5 por CDN en `base.html`; paleta en `static/css/estilos.css` (variables `--hb-mar`, `--hb-arena`…).

## 2. Diagramas y correcciones (2 min)
Abrir `docs/diagrama_actores.png` y `docs/diagrama_er.png` y explicar lo de `docs/LEEME.md`.

## 3. Modelos y relaciones (2 min)
- **1:N**: `TipoHabitacion → Habitacion` (`fk_hab_tipo`), `Huesped → Reserva`, `Habitacion → Reserva`.
- **N:M**: una reserva puede tener muchos servicios y un servicio estar en muchas reservas → tabla intermedia `ConsumoServicio` con datos propios (cantidad, valor, fecha).
- **Entidad débil**: `ConsumoServicio`, no existe sin la reserva (`on_delete=CASCADE`); al eliminar la reserva se borran sus consumos.
- Los catálogos usan `PROTECT`: no se puede borrar un huésped o habitación con reservas.

## 4. CRUD en vivo (3–4 min) — usuario `recepcion` / `Recepcion123`
1. **Listar**: `/reservas/` → buscar "Pushaina", filtrar por estado.
2. **Crear**: "Nueva reserva" → elegir huésped y habitación, fechas, "Agregar servicio" dos veces → mostrar el total en vivo → guardar.
3. Mostrar una **validación**: intentar reservar la misma habitación en fechas cruzadas → mensaje de error.
4. **Detalle**: datos del huésped, habitación, consumos y total. Hacer **check-in** (la habitación pasa a ocupada en el tablero).
5. **Editar**: cambiar la cantidad de un servicio, quitar otro y agregar uno nuevo.
6. **Eliminar**: página de confirmación que avisa que también se borran los consumos.

## 5. Funcionalidades adicionales (2 min)
- Entrar como `huesped` / `Huesped123`: menú reducido, solo ve sus reservas, puede solicitar y cancelar. Intentar abrir `/huespedes/` → página 403.
- Explicar `LoginRequiredMiddleware` (settings) y el decorador `@rol_requerido` (`usuarios/permisos.py`).
- Entrar como `admin` / `Admin12345`: tipos de habitación, reportes y el panel `/admin/` que sigue funcionando.

## Preguntas que pueden hacer
- *¿Dónde se valida que no se crucen reservas?* → `Reserva.clean()` en `reserva_core/models.py`.
- *¿Cómo se guardan los servicios junto con la reserva?* → `inlineformset_factory` en `reserva_core/forms.py`, guardado dentro de `transaction.atomic()` en `views.py`.
- *¿Cómo se sabe el rol?* → `tbl_perfil.per_rol`; el superusuario siempre es administrador (`rol_de()` en `permisos.py`).
- *¿Cómo se calcula el total?* → propiedades `noches`, `valor_alojamiento`, `valor_consumos` y `valor_total` del modelo `Reserva`.
