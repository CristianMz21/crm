"""Audit log model.

Every create/update/delete on a business model produces an
``AuditLog`` entry via ``post_save``/``post_delete`` signals.
The ``changes`` field stores a JSON diff of old vs new values.
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable record of a mutation on a business model."""

    ACTION_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
        verbose_name="actor",
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="action")
    model = models.CharField(max_length=80, verbose_name="model")
    object_id = models.PositiveBigIntegerField(verbose_name="object id")
    object_repr = models.CharField(max_length=255, verbose_name="object repr")
    changes = models.JSONField(default=dict, verbose_name="changes")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="timestamp")

    class Meta:
        verbose_name = "audit log"
        verbose_name_plural = "audit logs"
        ordering: ClassVar[list[str]] = ["-timestamp"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["model", "object_id"], name="audit_model_obj_idx"),
            models.Index(fields=["timestamp"], name="audit_timestamp_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.model}:{self.object_id}"
