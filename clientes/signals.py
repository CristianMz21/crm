"""Signal handlers for clientes app models.

Writes AuditLog entries on create/update/delete of Cliente,
Contacto, and Etiqueta.
"""

from __future__ import annotations

from typing import Any

from audit.services import compute_diff, log_action
from django.contrib.auth.models import User
from django.db.models import Model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from clientes.models import Cliente, Contacto, Etiqueta

_AUDITED_MODELS: list[type[Model]] = [Cliente, Contacto, Etiqueta]


def _get_actor(instance: Model) -> User | None:
    """Extract the actor from the instance, if available."""
    return getattr(instance, "_audit_actor", None)


def _make_handler(model_class: type[Model]) -> tuple[Any, Any]:
    """Build post_save and post_delete handlers for a given model."""

    @receiver(post_save, sender=model_class)
    def _post_save(
        sender: type[Model], instance: Model, created: bool, raw: bool, **kwargs: Any
    ) -> None:
        if raw or getattr(instance, "_skip_audit", False):
            return
        actor = _get_actor(instance)
        if created:
            from django.forms.models import model_to_dict

            log_action(
                actor=actor,
                action="create",
                instance=instance,
                changes={"new": model_to_dict(instance)},
            )
        else:
            diff = compute_diff(instance)
            if diff:
                log_action(
                    actor=actor,
                    action="update",
                    instance=instance,
                    changes=diff,
                )

    @receiver(post_delete, sender=model_class)
    def _post_delete(sender: type[Model], instance: Model, **kwargs: Any) -> None:
        if getattr(instance, "_skip_audit", False):
            return
        from django.forms.models import model_to_dict

        actor = _get_actor(instance)
        log_action(
            actor=actor,
            action="delete",
            instance=instance,
            changes={"old": model_to_dict(instance)},
        )

    return _post_save, _post_delete


# Register handlers for each audited model
for _model in _AUDITED_MODELS:
    _make_handler(_model)
