"""Core abstract models shared across all apps.

Every concrete business model inherits from one or more of these
to avoid duplicating timestamp, soft-delete, and audit fields.
"""

from typing import ClassVar

from django.db import models


class TimeStampedModel(models.Model):
    """Provides ``fecha_creacion`` and ``fecha_modificacion`` fields.

    Inherited by every concrete model that needs created/modified
    timestamps.  ``fecha_creacion`` is set once on insert;
    ``fecha_modificacion`` is refreshed on every ``save()``.
    """

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="fecha de modificación")

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Provides the ``activo`` flag for soft-delete.

    Concrete models that inherit this get a ``activo`` boolean
    (default ``True``).  The companion ``SoftDeleteManager``
    filters ``activo=True`` by default so archived records
    don't appear in normal querysets.
    """

    activo = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        abstract = True


class AuditModel(models.Model):
    """Provides the ``creado_por`` FK to track who created a record.

    Uses ``on_delete=PROTECT`` so that deleting a user never
    silently destroys business records they created.
    """

    creado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="creado por",
    )

    class Meta:
        abstract = True


class BusquedaGuardada(models.Model):
    """A named, saved filter on a list endpoint.

    Stores the endpoint name and the filter params as JSON so
    the user can re-run a search without re-entering all the
    query parameters.
    """

    nombre = models.CharField(max_length=100, verbose_name="nombre")
    endpoint = models.CharField(max_length=100, verbose_name="endpoint")
    filtros = models.JSONField(default=dict, verbose_name="filtros")
    creado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="busquedas_guardadas",
        verbose_name="creado por",
    )

    class Meta:
        verbose_name = "búsqueda guardada"
        verbose_name_plural = "búsquedas guardadas"
        unique_together: ClassVar[list[tuple[str, ...]]] = [
            ("endpoint", "nombre", "creado_por"),
        ]
        ordering: ClassVar[list[str]] = ["nombre"]

    def __str__(self) -> str:
        return self.nombre
