from django.apps import AppConfig


class PipelineConfig(AppConfig):
    name = "pipeline"

    def ready(self) -> None:
        from . import signals  # noqa: F401
