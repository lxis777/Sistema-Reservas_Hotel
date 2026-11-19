"""Vistas genéricas reutilizadas por los catálogos (tipos, habitaciones, servicios, huéspedes)."""
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.views import generic

from usuarios.permisos import RolRequeridoMixin


class ListaBuscableView(RolRequeridoMixin, generic.ListView):
    """Lista con buscador (?q=) y paginación."""
    paginate_by = 10
    campos_busqueda = ()
    filtros_exactos = ()  # parámetros GET que se aplican como filtro exacto

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q and self.campos_busqueda:
            condicion = Q()
            for campo in self.campos_busqueda:
                condicion |= Q(**{f"{campo}__icontains": q})
            qs = qs.filter(condicion)
        for campo in self.filtros_exactos:
            valor = self.request.GET.get(campo)
            if valor not in (None, ""):
                qs = qs.filter(**{campo: valor})
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["params"] = params.urlencode()
        return ctx


class CrearView(RolRequeridoMixin, SuccessMessageMixin, generic.CreateView):
    titulo = ""
    template_name = "comunes/formulario.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titulo=self.titulo, url_volver=self.success_url,
                   seccion=self.model._meta.verbose_name_plural)
        return ctx

    def form_invalid(self, form):
        messages.error(self.request, "El formulario tiene errores. Revisa los campos marcados.")
        return super().form_invalid(form)


class EditarView(RolRequeridoMixin, SuccessMessageMixin, generic.UpdateView):
    titulo = ""
    template_name = "comunes/formulario.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titulo=self.titulo, url_volver=self.success_url,
                   seccion=self.model._meta.verbose_name_plural)
        return ctx

    def form_invalid(self, form):
        messages.error(self.request, "El formulario tiene errores. Revisa los campos marcados.")
        return super().form_invalid(form)


class EliminarView(RolRequeridoMixin, generic.DeleteView):
    """Pide confirmación y maneja los registros protegidos (on_delete=PROTECT)."""
    template_name = "comunes/confirmar_eliminar.html"
    titulo = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titulo=self.titulo, url_volver=self.success_url,
                   seccion=self.model._meta.verbose_name_plural)
        return ctx

    def form_valid(self, form):
        nombre = str(self.object)
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, f"No se puede eliminar «{nombre}» porque tiene registros relacionados.")
            return redirect(self.success_url)
        messages.success(self.request, f"«{nombre}» se eliminó correctamente.")
        return redirect(self.success_url)
