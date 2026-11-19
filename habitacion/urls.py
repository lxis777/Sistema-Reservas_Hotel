from django.urls import path
from . import views

app_name = "habitaciones"

urlpatterns = [
    path("", views.Lista.as_view(), name="lista"),
    path("nueva/", views.Crear.as_view(), name="crear"),
    path("disponibilidad/", views.disponibilidad, name="disponibilidad"),
    path("<int:pk>/editar/", views.Editar.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.Eliminar.as_view(), name="eliminar"),
]
