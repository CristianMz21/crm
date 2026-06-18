"""Custom managers and querysets for soft-delete models.

``SoftDeleteManager`` filters ``activo=True`` by default so that
archived records don't appear in normal querysets.  To access
all records (including archived), use ``objects_all`` on the
concrete model.
"""

from __future__ import annotations

from typing import Self

from django.db import models


class SoftDeleteQuerySet(models.QuerySet["models.Model"]):
    """QuerySet with helpers for active/archived filtering."""

    def activos(self) -> Self:
        """Return only records where ``activo=True``."""
        return self.filter(activo=True)

    def archivados(self) -> Self:
        """Return only records where ``activo=False``."""
        return self.filter(activo=False)


class SoftDeleteManager(models.Manager["models.Model"]):
    """Default manager that hides archived records.

    Use ``Model.objects.activos()`` or ``Model.objects.archivados()``
    for explicit filtering.  ``Model.objects_all`` (a plain
    ``Manager``) returns everything including archived.
    """

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(activo=True)
