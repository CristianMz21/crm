# Spec 002: Business Models

**Branch**: `002-business-models`
**Depends on**: 001-core-foundation
**Blocks**: 003-services-audit (and everything downstream)

## What this delivers

All 7 concrete models + `BusquedaGuardada`, with their migrations
applied to the database. Each model inherits from the appropriate
`core` abstract models. Cross-app FKs are explicit.

## Deliverables

| Model | App | Inherits | Key fields |
|---|---|---|---|
| `Pipeline` | pipeline | TimeStamped | nombre, es_default |
| `Etapa` | pipeline | TimeStamped | pipeline FK, orden, cerrada, es_ganado |
| `AuditLog` | audit | (none) | actor, action, model, object_id, changes (JSON) |
| `Cliente` | clientes | TimeStamped + SoftDelete + Audit | nombre, email, ciudad, etiquetas M2M |
| `Contacto` | clientes | TimeStamped + SoftDelete + Audit | cliente FK, nombre, cargo |
| `Etiqueta` | clientes | TimeStamped | nombre (unique), color |
| `Oportunidad` | oportunidades | TimeStamped + SoftDelete + Audit | cliente FK, etapa FK, monto (Decimal), asignado_a FK |
| `Actividad` | oportunidades | TimeStamped + Audit | cliente FK, oportunidad FK (nullable), tipo, nota |
| `BusquedaGuardada` | core | (none) | nombre, endpoint, filtros (JSON), creado_por FK |

## Acceptance criteria

1. `python manage.py makemigrations --check --dry-run` → "No changes detected"
2. `python manage.py migrate` → all migrations apply cleanly
3. `Oportunidad._meta.get_field('monto').__class__.__name__` → `DecimalField`
4. `Cliente._meta.get_field('etiquetas').__class__.__name__` → `ManyToManyField`
5. `Etapa` has a unique constraint on `(pipeline, orden)`
6. `AuditLog` has indexes on `(model, object_id)` and `timestamp`
7. `Cliente.objects` returns only `activo=True` (SoftDeleteManager)
8. `Cliente.objects_all` returns everything
9. `python manage.py check` → 0 issues
10. `ruff check .` passes

## Spec references

- [data-model.md](../000-architecture/data-model.md) → all entity sections + decisions D-1 through D-9
- [ADR-001](../000-architecture/adr-001-bounded-context-apps.md) → app structure
