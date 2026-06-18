import importlib

from django.apps import AppConfig


class OportunidadesConfig(AppConfig):
    name = "oportunidades"

    def ready(self) -> None:
        importlib.import_module(f"{self.name}.signals")
