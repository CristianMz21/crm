# ADR-001: Bounded context app structure (6 apps)

**Date**: 2026-06-18  
**Status**: Accepted  
**Supersedes**: Plan section "Project Structure" (4 apps)

## Context

The original plan specified 4 Django apps: `clientes`, `pipeline`,
`audit`, `dashboard`. The `clientes` app held 5 models (Cliente,
Contacto, Oportunidad, Actividad, Etiqueta), which mixed two
bounded contexts: contact management and sales pipeline.

The user asked to evaluate the best architecture for a project
that may grow. The evaluation considered:

- What happens when the CRM adds campaigns, quotes, contracts?
- Where do shared abstractions (timestamped, soft-delete, audit
  mixin) live without duplicating code?
- How do cross-entity concerns (saved searches, audit log) get
  modeled without forcing one app to know about all others?

## Decision

Split into 6 apps, organized by bounded context:

| App | Bounded context | Models | Growth direction |
|---|---|---|---|
| `core` | Shared infrastructure | `BusquedaGuardada` + abstract base models (`TimeStampedModel`, `SoftDeleteModel`, `AuditModel`) | New shared abstractions go here |
| `clientes` | Contact management | `Cliente`, `Contacto`, `Etiqueta` | Tags, contact groups, import/export |
| `oportunidades` | Sales pipeline | `Oportunidad`, `Actividad` | Forecasting, quotes, line items |
| `pipeline` | Pipeline configuration | `Pipeline`, `Etapa` | Multiple pipelines, stage transitions, automations |
| `audit` | Audit & compliance | `AuditLog` | Retention policies, export, compliance reports |
| `dashboard` | Analytics & reporting | (no models) | Charts, scheduled reports, KPIs |

## Rationale

1. **`core` prevents duplication.** Without it, `fecha_creacion`,
   `fecha_modificacion`, `activo`, and `creado_por` are copy-pasted
   across 7+ models. With abstract base models in `core`, each
   concrete model inherits them and adds only its own fields.

2. **`oportunidades` separated from `clientes`** because the sales
   pipeline is a different bounded context. Contacts are about
   "who do I know"; opportunities are about "what am I selling".
   The coupling is a FK (`Oportunidad.cliente → clientes.Cliente`),
   not a shared lifecycle. When forecasting, assignment, or
   commission logic lands, it lives in `oportunidades`, not
   bloating `clientes`.

3. **Future features get their own apps.** When `campanas`,
   `cotizaciones`, or `contratos` arrive, they are new apps with
   FKs to `clientes` and `oportunidades`. They do not get stuffed
   into an existing app.

4. **`dashboard` has no models.** It is a read-only projection of
   data from other apps. Keeping it model-free prevents it from
   becoming a dumping ground.

5. **`audit` is cross-cutting.** It listens to signals from all
   business apps but owns no business logic. Its independence makes
   it easy to add retention policies or compliance exports later.

## Consequences

- **Positive**: each app has a clear purpose; new features know
  where to land; shared code is DRY via `core` abstract models.
- **Positive**: cross-app FKs are explicit, which makes the data
  model easier to reason about.
- **Negative**: 6 apps instead of 4 means more `INSTALLED_APPS`
  entries and more `urls.py` files. Acceptable: the overhead is
  linear, the clarity is superlinear.
- **Negative**: the existing `clientes/migrations/0001_initial.py`
  creates `Cliente` and `Contacto`. This migration stays valid.
  Future models (`Oportunidad`, `Actividad`) get new migrations
  in the `oportunidades` app. No data migration needed.

## Migration from the 4-app plan

- `clientes.Oportunidad` → `oportunidades.Oportunidad` (new app)
- `clientes.Actividad` → `oportunidades.Actividad` (new app)
- `clientes.BusquedaGuardada` → `core.BusquedaGuardada` (new app)
- `clientes.Etiqueta` stays in `clientes`
- `core` is new: abstract base models + `BusquedaGuardada`

The spec files (`data-model.md`, `plan.md`, `tasks.md`) are
updated to reflect these new paths.
