from django.apps import AppConfig


class OportunidadesConfig(AppConfig):
    name = "oportunidades"

    def ready(self):
        from . import signals  # noqa: F401
