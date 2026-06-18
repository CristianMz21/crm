"""Seed the default pipeline with 4 stages.

Creates Pipeline Default with stages: Nuevo, En proceso, Ganado, Perdido.
Idempotent: skips if any pipelines already exist.
"""

from __future__ import annotations

from typing import Any

from django.db import migrations


def seed_pipeline(apps: Any, schema_editor: Any) -> None:
    Pipeline = apps.get_model("pipeline", "Pipeline")
    Etapa = apps.get_model("pipeline", "Etapa")

    if Pipeline.objects.exists():
        return

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


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0002_etapa"),
    ]

    operations = [
        migrations.RunPython(seed_pipeline, migrations.RunPython.noop),
    ]
