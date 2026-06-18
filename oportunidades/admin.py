from django.contrib import admin

from oportunidades.models import Actividad, Oportunidad


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    list_display = ("titulo", "cliente", "monto", "etapa", "asignado_a", "fecha_cierre")
    search_fields = ("titulo",)
    list_filter = ("etapa", "asignado_a")
    raw_id_fields = ("cliente", "etapa", "asignado_a", "creado_por")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("tipo", "cliente", "oportunidad", "fecha_creacion")
    list_filter = ("tipo",)
    raw_id_fields = ("cliente", "oportunidad", "creado_por")
