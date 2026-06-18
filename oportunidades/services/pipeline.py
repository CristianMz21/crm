"""Pipeline business services.

Functions for creating and moving opportunities through pipeline
stages.  These are the canonical entry points — views and signals
call these rather than manipulating models directly.
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth.models import User
from pipeline.models import Etapa, Pipeline

from oportunidades.models import Oportunidad


def ensure_default_pipeline() -> Pipeline:
    """Create the default pipeline with 4 stages if it doesn't exist.

    Stages: Nuevo, En proceso, Ganado, Perdido.
    Idempotent: if a default pipeline already exists, returns it.

    Returns:
        Pipeline: the default pipeline.
    """
    existing = Pipeline.objects.filter(es_default=True).first()
    if existing:
        return existing

    pipeline = Pipeline.objects.create(
        nombre="Pipeline Default",
        descripcion="Pipeline por defecto con 4 etapas",
        es_default=True,
    )

    etapas = [
        Etapa(pipeline=pipeline, nombre="Nuevo", orden=0),
        Etapa(pipeline=pipeline, nombre="En proceso", orden=1),
        Etapa(
            pipeline=pipeline,
            nombre="Ganado",
            orden=2,
            cerrada=True,
            es_ganado=True,
            color="#28a745",
        ),
        Etapa(
            pipeline=pipeline,
            nombre="Perdido",
            orden=3,
            cerrada=True,
            color="#dc3545",
        ),
    ]
    Etapa.objects.bulk_create(etapas)
    return pipeline


def mover_etapa(
    oportunidad: Oportunidad,
    etapa_id: int,
    *,
    actor: User | None = None,
) -> Oportunidad:
    """Move an opportunity to a new pipeline stage.

    Automatically sets ``fecha_cierre`` when moving to a closed
    stage (Ganado/Perdido) and clears it when moving back to an
    open stage.

    Args:
        oportunidad: the Oportunidad instance to move.
        etapa_id: the target Etapa primary key.
        actor: the User performing the move (for audit logging).

    Returns:
        Oportunidad: the updated opportunity.

    Raises:
        ValueError: if the target etapa belongs to a different
            pipeline than the opportunity's current etapa.
        Etapa.DoesNotExist: if no etapa with ``etapa_id`` exists.
    """
    nueva_etapa = Etapa.objects.get(pk=etapa_id)

    if oportunidad.etapa_id and nueva_etapa.pipeline_id != oportunidad.etapa.pipeline_id:
        raise ValueError(
            f"La etapa '{nueva_etapa.nombre}' pertenece al pipeline "
            f"'{nueva_etapa.pipeline.nombre}', no al pipeline de la "
            f"oportunidad."
        )

    oportunidad.etapa = nueva_etapa

    if nueva_etapa.cerrada:
        oportunidad.fecha_cierre = date.today()
    else:
        oportunidad.fecha_cierre = None

    oportunidad.save()
    return oportunidad
