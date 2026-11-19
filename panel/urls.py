from django.urls import path
from . import views

app_name = "panel"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("reportes/", views.reportes, name="reportes"),
]
