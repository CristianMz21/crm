"""Core abstract models shared across all apps.

Every concrete business model inherits from one or more of these
to avoid duplicating timestamp, soft-delete, and audit fields.
"""

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
