"""Sales pipeline models.

``Oportunidad`` is a deal attached to a client. ``Actividad`` is an
interaction log entry. Both inherit from core abstract models.
"""

from core.managers import SoftDeleteManager
from core.models import AuditModel, SoftDeleteModel, TimeStampedModel
from django.conf import settings
from django.db import models


class Oportunidad(TimeStampedModel, SoftDeleteModel, AuditModel):
    """A sales deal attached to a ``Cliente`` and a pipeline ``Etapa``."""

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="oportunidades",
        verbose_name="cliente",
    )
    titulo = models.CharField(max_length=200, verbose_name="título")
    descripcion = models.TextField(blank=True, verbose_name="descripción")
    monto = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="monto")
    etapa = models.ForeignKey(
        "pipeline.Etapa",
        on_delete=models.PROTECT,
        related_name="oportunidades",
        verbose_name="etapa",
    )
    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="oportunidades",
        verbose_name="asignado a",
    )
    fecha_cierre = models.DateField(null=True, blank=True, verbose_name="fecha de cierre")

    objects = SoftDeleteManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = "oportunidad"
        verbose_name_plural = "oportunidades"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo


class Actividad(TimeStampedModel, AuditModel):
    """An interaction log entry (call, email, meeting).

    Note: does NOT inherit ``SoftDeleteModel`` — activities are
    never archived.  ``oportunidad`` uses ``SET_NULL`` so that
    deleting an opportunity keeps the activity note.
    """

    TIPO_CHOICES = [
        ("llamada", "Llamada"),
        ("email", "Email"),
        ("reunion", "Reunión"),
    ]

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.CASCADE,
        related_name="actividades",
        verbose_name="cliente",
    )
    oportunidad = models.ForeignKey(
        Oportunidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades",
        verbose_name="oportunidad",
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="tipo")
    nota = models.TextField(verbose_name="nota")

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.tipo}: {self.cliente.nombre}"
