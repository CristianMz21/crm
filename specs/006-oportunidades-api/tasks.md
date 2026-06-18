# Tasks: 006-oportunidades-api

**Spec**: [spec.md](./spec.md) | **Ref**: [api.yaml](../000-architecture/contracts/api.yaml)

---

## S045 — EtapaSerializer + PipelineSerializer

**File**: `pipeline/api/serializers.py`

`EtapaSerializer`: id, pipeline, nombre, orden, cerrada, es_ganado, color.
`PipelineSerializer`: id, nombre, descripcion, es_default, `etapas = EtapaSerializer(many=True, read_only=True)`.

- [ ] S045 done

---

## S046 — PipelineViewSet + EtapaViewSet

**File**: `pipeline/api/views.py`

`PipelineViewSet(ModelViewSet)` with `@action(detail=False)` `default()` returning the default pipeline.
`EtapaViewSet(ModelViewSet)`.

- [ ] S046 done

---

## S047 — Register pipeline routes

**File**: `pipeline/api/urls.py`

Register both viewsets.

**Verify**: `python manage.py check`
- [ ] S047 done

---

## S048 — OportunidadSerializer

**File**: `oportunidades/api/serializers.py`

`OportunidadSerializer(ModelSerializer)`: all fields. `monto` as string (DRF default for Decimal). `etapa` as nested EtapaSerializer (read-only). `validate()`: if etapa is cerrada+es_ganado and no fecha_cierre → ValidationError.

- [ ] S048 done

---

## S049 — OportunidadFilter

**File**: `oportunidades/api/filters.py`

`OportunidadFilter(FilterSet)`: etapa (FK exact), cliente (FK exact), asignado_a (FK exact), monto__gte (NumberFilter), monto__lte (NumberFilter), search (method → titulo__icontains).

- [ ] S049 done

---

## S050 — OportunidadViewSet

**File**: `oportunidades/api/views.py`

`ModelViewSet`: filterset_class = OportunidadFilter. `@action(detail=True, methods=["post"])` `mover_etapa(request)` calling `oportunidades.services.pipeline.mover_etapa(oportunidad, etapa_id, actor=request.user)`. `perform_destroy()` → soft delete.

- [ ] S050 done

---

## S051 — Register oportunidades routes

**File**: `oportunidades/api/urls.py`

Register `OportunidadViewSet`.

**Verify**: `python manage.py check`
- [ ] S051 done

---

## S052 — API tests

**File**: `oportunidades/tests/test_api_oportunidades.py`

9 tests: create 201, create without monto 400, mover to ganado sets fecha_cierre, mover to perdido sets fecha_cierre, mover from cerrado clears fecha_cierre, filter by etapa, filter by monto range, filter by asignado_a, list paginated.

**Verify**: `uv run pytest oportunidades/tests/test_api_oportunidades.py -v` → 9 passed
- [ ] S052 done

---

## S053 — Pipeline tests

**File**: `pipeline/tests/test_pipeline.py`

Tests: ensure_default_pipeline creates 4 etapas, idempotent, cannot have 2 defaults, etapas ordered by orden.

**Verify**: `uv run pytest pipeline/tests/test_pipeline.py -v` → 4 passed
- [ ] S053 done

---

## S054 — N+1 tests for oportunidades

**File**: `oportunidades/tests/test_orm.py`

`assertNumQueries` for oportunidades list and detail.

**Verify**: `uv run pytest oportunidades/tests/test_orm.py -v` → 2 passed
- [ ] S054 done

---

## S055 — Checkpoint

```bash
uv run pytest oportunidades/tests/ pipeline/tests/ -v
uv run python manage.py check
uv run ruff check .
```

All pass → US3a done. Pipeline + Oportunidades API ready.

- [ ] S055 US3a checkpoint passed ✅
