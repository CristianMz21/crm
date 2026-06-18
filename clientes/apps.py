import importlib

from django.apps import AppConfig


class ClientesConfig(AppConfig):
    name = "clientes"

    def ready(self) -> None:
        importlib.import_module(f"{self.name}.signals")
