# Spec 003: Services, Signals, Admin & Seed

**Branch**: `003-services-audit`
**Depends on**: 002-business-models
**Blocks**: 004-auth, 005-clientes-api, 006-oportunidades-api

## What this delivers

The business logic layer (services), the cross-cutting audit signals,
the admin registrations, and the data migration that seeds the
default pipeline. After this spec, the foundation is complete and
user-story work can begin.

## Deliverables

- `oportunidades.services.pipeline.ensure_default_pipeline()` — idempotent, creates 4 stages
- `oportunidades.services.pipeline.mover_etapa()` — moves opportunity, auto-sets fecha_cierre
- `audit.services.log_action()` — creates AuditLog entry
- `audit.services.compute_diff()` — computes old/new diff for updates
- `post_save` + `post_delete` signals on 5 business models → audit log
- `pre_save` signal on Pipeline → single default enforcement
- Signal registration in `apps.py:ready()` for 3 apps
- Data migration seeding the default pipeline
- Admin registrations for all 8 concrete models

## Acceptance criteria

1. `ensure_default_pipeline()` creates a pipeline with exactly 4 etapas
2. Calling it twice doesn't create duplicates (idempotent)
3. `mover_etapa()` to a `cerrada=True` etapa sets `fecha_cierre`
4. `mover_etapa()` to a `cerrada=False` etapa clears `fecha_cierre`
5. Creating a `Cliente` produces an `AuditLog` entry with `action="create"`
6. Updating a `Cliente` produces an `AuditLog` entry with `action="update"` and a diff
7. Creating a second `Pipeline` with `es_default=True` unsets the first
8. `python manage.py migrate` seeds the default pipeline
9. All 8 models are visible in `/admin/`
10. `python manage.py check` → 0 issues

## Spec references

- [data-model.md](../000-architecture/data-model.md) → D-5, D-7, D-8
- [constitution](../../.specify/memory/constitution.md) → principle VI (validation), VII (no silent failures)
