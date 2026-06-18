from django.contrib import admin

from pipeline.models import Etapa, Pipeline


class EtapaInline(admin.TabularInline):
    model = Etapa
    extra = 1
    ordering = ("orden",)


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("nombre", "es_default", "descripcion")
    list_filter = ("es_default",)
    inlines = [EtapaInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "pipeline", "orden", "cerrada", "es_ganado", "color")
    list_filter = ("pipeline", "cerrada", "es_ganado")
    raw_id_fields = ("pipeline",)
