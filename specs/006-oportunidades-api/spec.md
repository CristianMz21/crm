# Spec 006: Oportunidades API (US3a)

**Branch**: `006-oportunidades-api`
**Depends on**: 005-clientes-api (Oportunidad FKs to Cliente)
**Blocks**: 007-dashboard
**User story**: US3 — Move opportunities through a pipeline (P1 MVP)

## What this delivers

Full CRUD API for `Oportunidad` with pipeline filtering, the
`mover_etapa` custom action that auto-manages `fecha_cierre`,
pipeline/etapa viewsets for reading the pipeline configuration,
and N+1-free queries.

## Deliverables

- `EtapaSerializer`, `PipelineSerializer`
- `PipelineViewSet` with `default` action, `EtapaViewSet`
- `OportunidadSerializer` with cross-field validation
- `OportunidadFilter` (etapa, cliente, asignado_a, monto range, search)
- `OportunidadViewSet` with `mover_etapa` action
- Tests: 9 API tests + 2 pipeline tests + 2 N+1 tests

## Acceptance criteria

1. POST `/api/oportunidades/` with valid data → 201
2. POST without monto → 400
3. POST `/api/oportunidades/<id>/mover_etapa/` to Ganado → 200, `fecha_cierre` set
4. Mover to Perdido → `fecha_cierre` set
5. Mover from cerrado back to abierta → `fecha_cierre` cleared
6. GET `?etapa=2` → only opportunities in etapa 2
7. GET `?monto__gte=1000&monto__lte=10000` → range filter
8. GET `?asignado_a=1` → filter by user
9. GET `/api/pipelines/default/` → the default pipeline with 4 etapas
10. `assertNumQueries` on list and detail are bounded
11. `ensure_default_pipeline` creates 4 etapas, idempotent
12. Cannot have 2 default pipelines
13. `pytest` all pass + `ruff check .` passes

## Spec references

- [spec.md](../000-architecture/spec.md) → User Story 3
- [contracts/api.yaml](../000-architecture/contracts/api.yaml) → `/api/oportunidades/*`, `/api/pipelines/*`
- [data-model.md](../000-architecture/data-model.md) → oportunidades.Oportunidad, pipeline.Pipeline, pipeline.Etapa
