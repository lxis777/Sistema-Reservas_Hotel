from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nueva/", views.crear, name="crear"),
    path("solicitar/", views.solicitar, name="solicitar"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
    path("<int:pk>/estado/<str:accion>/", views.cambiar_estado, name="estado"),
]
