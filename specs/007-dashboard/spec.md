# Spec 007: Dashboard (US3b)

**Branch**: `007-dashboard`
**Depends on**: 006-oportunidades-api
**Blocks**: nothing — this completes the MVP
**User story**: US3 — Dashboard metrics (P1 MVP)

## What this delivers

A read-only `/api/dashboard/` endpoint that returns aggregated
metrics: pipeline value per stage, won/lost totals for the current
month, win rate, and top 5 open opportunities by amount.

## Deliverables

- `dashboard.services.compute_dashboard_metrics()` — all aggregations in bounded queries
- `dashboard.api.views.DashboardView` — GET only, returns the metrics dict
- Tests: 5 tests covering all metrics + empty state

## Acceptance criteria

1. GET `/api/dashboard/` → 200 with `pipeline_por_etapa`, `ganado_mes_actual`, `perdido_mes_actual`, `win_rate`, `top_5_abiertos`
2. `pipeline_por_etapa` is a list of `{etapa, total, cantidad}` per stage
3. `ganado_mes_actual` is the Sum of monto where etapa.es_ganado and fecha_cierre this month
4. `win_rate` = ganado / (ganado + perdido), 0 if no closed deals
5. Empty database → 200 with zeros, not 500
6. Each metric is computed in a single query (no Python-side loops)
7. `pytest` all pass + `ruff check .` passes

## Spec references

- [spec.md](../000-architecture/spec.md) → User Story 3 (dashboard part) + User Story 8
- [contracts/api.yaml](../000-architecture/contracts/api.yaml) → `/api/dashboard/`
