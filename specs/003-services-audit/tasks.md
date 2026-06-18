# Tasks: 003-services-audit

**Spec**: [spec.md](./spec.md) | **Ref**: [data-model.md](../000-architecture/data-model.md) → D-5, D-7, D-8

---

## S020 — ensure_default_pipeline()

**File**: `oportunidades/services/pipeline.py`
**Spec ref**: data-model.md → D-7

Function that creates a default Pipeline (es_default=True) with 4 Etapas: Nuevo (orden=0), En proceso (orden=1), Ganado (orden=2, cerrada=True, es_ganado=True), Perdido (orden=3, cerrada=True). Idempotent.

**Verify**: `shell -c "from oportunidades.services.pipeline import ensure_default_pipeline; p = ensure_default_pipeline(); print(p.nombre, p.etapas.count())"` → `(name) 4`
- [ ] S020 done

---

## S021 — mover_etapa()

**File**: `oportunidades/services/pipeline.py`
**Spec ref**: data-model.md → D-8

`mover_etapa(oportunidad, etapa_id, *, actor=None)`: sets etapa, sets/clears fecha_cierre based on `cerrada`, calls `save()`. Raises `ValueError` if etapa belongs to different pipeline.

**Verify**: create oportunidad in Nuevo, move to Ganado, check `fecha_cierre is not None`
- [ ] S021 done

---

## S022 — log_action()

**File**: `audit/services/__init__.py`
**Spec ref**: data-model.md → audit.AuditLog

`log_action(*, actor, action, instance, changes)`: creates AuditLog with model=`instance.__class__._meta.label`, object_id=`instance.pk`, object_repr=`str(instance)`.

**Verify**: `shell -c "from audit.services import log_action; print(callable(log_action))"` → `True`
- [ ] S022 done

---

## S023 — compute_diff()

**File**: `audit/services/__init__.py`
**Spec ref**: data-model.md → D-5

`compute_diff(instance)`: re-fetches instance from DB, compares fields, returns `{field: {old, new}}` for changed fields. Excludes `fecha_creacion`, `fecha_modificacion`.

**Verify**: `shell -c "from audit.services import compute_diff; print(callable(compute_diff))"` → `True`
- [ ] S023 done

---

## S024 — post_save signals for audit

**Files**: `clientes/signals.py`, `oportunidades/signals.py`
**Spec ref**: data-model.md → D-5

`post_save` handlers for Cliente, Contacto, Etiqueta (in clientes) and Oportunidad, Actividad (in oportunidades). On `created=True`: log create. On `created=False`: compute_diff, if non-empty log update. Skip if `raw` or `instance._skip_audit`.

**Verify**: create a Cliente, check `AuditLog.objects.filter(model="clientes.Cliente").count()` → 1
- [ ] S024 done

---

## S025 — post_delete signals for audit

**Files**: `clientes/signals.py`, `oportunidades/signals.py`

`post_delete` handlers for same 5 models. Log delete with `changes={"old": model_to_dict(instance)}`.

**Verify**: hard-delete a Cliente via `objects_all`, check AuditLog has delete entry
- [ ] S025 done

---

## S026 — Register signals in apps.py:ready()

**Files**: `clientes/apps.py`, `oportunidades/apps.py`, `pipeline/apps.py`

`def ready(self): from . import signals  # noqa: F401`

**Verify**: `python manage.py check` → no AppRegistryNotReady
- [ ] S026 done

---

## S027 — pre_save signal: single default pipeline

**File**: `pipeline/signals.py`
**Spec ref**: data-model.md → D-7

`pre_save` on Pipeline: if `instance.es_default=True`, set `es_default=False` on all other pipelines.

**Verify**: create 2 pipelines with es_default=True, check only 1 has it
- [ ] S027 done

---

## S028 — Data migration: seed default pipeline

**File**: `oportunidades/migrations/0002_seed_default_pipeline.py`
**Spec ref**: plan.md → Migration strategy

Data migration calling `ensure_default_pipeline()` in `forwards()`. `reverse()` deletes the seeded pipeline.

**Verify**: `migrate` + `shell -c "from pipeline.models import Pipeline; print(Pipeline.objects.filter(es_default=True).count())"` → 1
- [ ] S028 done

---

## S029 — Admin registrations

**Files**: `clientes/admin.py`, `oportunidades/admin.py`, `pipeline/admin.py`, `audit/admin.py`, `core/admin.py`

Register every concrete model. Use `list_display`, `list_filter`, `search_fields`. AuditLog is read-only.

**Verify**: `python manage.py check` + visit `/admin/`
- [ ] S029 done

---

## S030 — Checkpoint

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py shell -c "
from oportunidades.services.pipeline import ensure_default_pipeline, mover_etapa
from audit.services import log_action, compute_diff
p = ensure_default_pipeline()
print(f'Pipeline: {p.nombre}, etapas: {p.etapas.count()}')
print('Foundation ready')
"
uv run ruff check .
uv run ruff format --check .
```

All pass → foundation complete. US1, US2, US3 can begin.

- [ ] S030 foundation checkpoint passed ✅
