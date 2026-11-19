from django.urls import path
from . import views

app_name = "servicios"

urlpatterns = [
    path("", views.Lista.as_view(), name="lista"),
    path("nuevo/", views.Crear.as_view(), name="crear"),
    path("<int:pk>/editar/", views.Editar.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.Eliminar.as_view(), name="eliminar"),
]
