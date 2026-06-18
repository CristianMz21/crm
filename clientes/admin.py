from django.contrib import admin

from clientes.models import Cliente, Contacto, Etiqueta


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "empresa", "pais", "creado_por")
    search_fields = ("nombre", "email", "empresa")
    list_filter = ("pais",)
    raw_id_fields = ("creado_por",)
    filter_horizontal = ("etiquetas",)


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "cargo", "cliente")
    search_fields = ("nombre", "email")
    raw_id_fields = ("cliente", "creado_por")


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color")
    search_fields = ("nombre",)
