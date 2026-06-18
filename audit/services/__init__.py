"""Audit log services.

Functions for creating audit log entries and computing diffs
between old and new model states.  Called by ``post_save`` and
``post_delete`` signal handlers in each business app.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from audit.models import AuditLog

# Fields that are auto-managed and should not appear in diffs.
_DIFF_EXCLUDE_FIELDS = frozenset({"fecha_creacion", "fecha_modificacion", "id"})


def log_action(
    *,
    actor: User | None,
    action: str,
    instance: Any,
    changes: dict[str, Any],
) -> None:
    """Create an AuditLog entry for a model mutation.

    Args:
        actor: the User who triggered the action (or None for
            system actions).
        action: one of "create", "update", "delete".
        instance: the model instance that was mutated.
        changes: a dict describing the change.  For create:
            ``{"new": {...}}``.  For update: ``{field: {old, new}}``.
            For delete: ``{"old": {...}}``.
    """
    AuditLog.objects.create(
        actor=actor,
        action=action,
        model=instance.__class__._meta.label,
        object_id=instance.pk,
        object_repr=str(instance)[:255],
        changes=changes,
    )


def compute_diff(instance: Any) -> dict[str, dict[str, Any]]:
    """Compute the field-level diff between DB and current instance.

    Re-fetches the instance from the database and compares each
    field.  Returns a dict of ``{field: {"old": ..., "new": ...}}``
    for fields that changed.  Excludes auto-managed fields.

    Args:
        instance: the model instance that was modified (but not
            yet saved, or just saved).

    Returns:
        dict: empty dict if nothing changed, otherwise
            ``{field_name: {"old": old_value, "new": new_value}}``.
    """
    if instance.pk is None:
        return {}

    try:
        db_instance = instance.__class__.objects_all.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return {}

    old_dict = model_to_dict(db_instance)
    new_dict = model_to_dict(instance)

    diff: dict[str, dict[str, Any]] = {}
    for field_name, new_value in new_dict.items():
        if field_name in _DIFF_EXCLUDE_FIELDS:
            continue
        old_value = old_dict.get(field_name)
        if old_value != new_value:
            diff[field_name] = {"old": old_value, "new": new_value}

    return diff
