"""Pipeline configuration models.

A ``Pipeline`` is a named collection of ordered ``Etapa`` stages.
Exactly one pipeline is marked as default (enforced by signal in
``pipeline/signals.py``).
"""

from __future__ import annotations

from core.models import TimeStampedModel
from django.db import models


class Pipeline(TimeStampedModel):
    """A named sales pipeline containing ordered stages."""

    nombre = models.CharField(max_length=100, unique=True, verbose_name="nombre")
    descripcion = models.TextField(blank=True, verbose_name="descripción")
    es_default = models.BooleanField(default=False, verbose_name="es default")

    class Meta:
        verbose_name = "pipeline"
        verbose_name_plural = "pipelines"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Etapa(TimeStampedModel):
    """A stage within a pipeline, ordered by ``orden``.

    ``cerrada=True`` marks terminal stages (Ganado, Perdido).
    ``es_ganado=True`` distinguishes won from lost.
    """

    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name="etapas",
        verbose_name="pipeline",
    )
    nombre = models.CharField(max_length=50, verbose_name="nombre")
    orden = models.PositiveIntegerField(verbose_name="orden")
    cerrada = models.BooleanField(default=False, verbose_name="cerrada")
    es_ganado = models.BooleanField(default=False, verbose_name="es ganado")
    color = models.CharField(max_length=7, blank=True, default="", verbose_name="color")

    class Meta:
        verbose_name = "etapa"
        verbose_name_plural = "etapas"
        ordering = ["pipeline", "orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["pipeline", "orden"],
                name="unique_orden_per_pipeline",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.pipeline.nombre} > {self.nombre}"
