from django.apps import AppConfig


class ClientesConfig(AppConfig):
    name = "clientes"

    def ready(self):
        from . import signals  # noqa: F401
