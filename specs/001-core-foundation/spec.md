# Spec 001: Core Foundation

**Branch**: `001-core-foundation`
**Depends on**: nothing
**Blocks**: 002-business-models (and everything downstream)

## What this delivers

Three abstract base models and a custom manager that every concrete
model in the project inherits from. No database tables are created
(abstract models don't migrate). This is the DRY foundation that
prevents duplicating `fecha_creacion`, `activo`, and `creado_por`
across 7+ models.

## Deliverables

- `core.models.TimeStampedModel` — abstract, `fecha_creacion` + `fecha_modificacion`
- `core.models.SoftDeleteModel` — abstract, `activo` boolean
- `core.models.AuditModel` — abstract, `creado_por` FK to User
- `core.managers.SoftDeleteManager` — filters `activo=True` by default
- `core.managers.SoftDeleteQuerySet` — `activos()` and `archivados()` methods

## Acceptance criteria

1. `TimeStampedModel._meta.abstract` is `True`
2. `SoftDeleteModel._meta.abstract` is `True`
3. `AuditModel._meta.abstract` is `True`
4. `SoftDeleteManager` returns only `activo=True` records by default
5. `SoftDeleteQuerySet.activos()` returns active records
6. `SoftDeleteQuerySet.archivados()` returns archived records
7. `python manage.py makemigrations core` outputs "No changes detected"
8. `python manage.py check` passes with 0 issues
9. `ruff check core/` passes
10. `ruff format --check core/` passes

## Spec references

- [data-model.md](../000-architecture/data-model.md) → `core.TimeStampedModel`, `core.SoftDeleteModel`, `core.AuditModel`, D-4
- [constitution](../../.specify/memory/constitution.md) → principle IV (soft delete), principle I (spec-first)
