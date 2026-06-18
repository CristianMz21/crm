import importlib

from django.apps import AppConfig


class PipelineConfig(AppConfig):
    name = "pipeline"

    def ready(self) -> None:
        importlib.import_module(f"{self.name}.signals")
