# Sistema de Reservas de Hotel — Proyecto 8

Aplicación académica Django para gestionar tipos de habitación, habitaciones, huéspedes, reservas, servicios y consumos adicionales.

## Requisitos
- Python 3.10 o superior
- pip

## Instalación (Windows)
```bash
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations tipo_habitacion_core habitacion huesped reserva_core servicio consumo_servicio
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Abrir `http://127.0.0.1:8000/admin/` e iniciar sesión con el superusuario creado.

## Instalación (macOS / Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations tipo_habitacion_core habitacion huesped reserva_core servicio consumo_servicio
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Aplicaciones y entidades
- `tipo_habitacion_core`: tipos de habitación.
- `habitacion`: habitaciones del hotel.
- `huesped`: datos de huéspedes.
- `reserva_core`: reservas y fechas de estadía.
- `servicio`: catálogo de servicios adicionales.
- `consumo_servicio`: tabla intermedia/débil que registra servicio, cantidad y fecha por reserva.

## Relaciones
- TipoHabitacion 1:N Habitacion.
- Huesped 1:N Reserva.
- Habitacion 1:N Reserva.
- Reserva N:M Servicio mediante ConsumoServicio.
- ConsumoServicio depende de Reserva y registra cantidad y fecha.

El modelo valida que la fecha de salida sea posterior a la entrada. Los consumos de servicio se pueden agregar dentro del formulario de reserva mediante un inline.

## Diagramas
Los diagramas se encuentran en `docs/diagrama_actores.png` y `docs/diagrama_er.png`.

## Datos de prueba
Después de migrar, ingrese al menos 3 registros por cada tabla desde `/admin/`. Orden recomendado: tipos de habitación, habitaciones, huéspedes, servicios, reservas y consumos de servicios. Cree el usuario administrador con `createsuperuser`; por seguridad no se incluyen credenciales fijas.
