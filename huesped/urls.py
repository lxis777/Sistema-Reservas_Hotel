from django.urls import path
from . import views

app_name = "huespedes"

urlpatterns = [
    path("", views.Lista.as_view(), name="lista"),
    path("nuevo/", views.Crear.as_view(), name="crear"),
    path("<int:pk>/", views.Detalle.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.Editar.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.Eliminar.as_view(), name="eliminar"),
]
