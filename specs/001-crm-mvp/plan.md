# Implementation Plan: CRM MVP

**Branch**: `001-crm-mvp` | **Date**: 2026-06-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-crm-mvp/spec.md`
plus the data model in `data-model.md` and the research in
`research.md`.

## Summary

Build a real, productive CRM for a single owner. The system manages
clients, their contacts, opportunities in a pipeline with stages,
an activities log, an audit log, advanced filtering, CSV export,
and a dashboard with basic metrics. It is a Django 6 + DRF project
managed with the spec-kit methodology.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Django 6.0, Django REST Framework 3.17,
django-filter 24+, django-debug-toolbar 4+, pytest 8+,
pytest-django 4.8+, Faker 25+
**Storage**: SQLite (dev + tests), PostgreSQL-ready (no
SQLite-specific behavior)
**Testing**: pytest + pytest-django, `assertNumQueries` for N+1
regression
**Target Platform**: Linux server (single host, single user in v1)
**Project Type**: Web application (Django backend + DRF API,
minimal HTML templates, no SPA)
**Performance Goals**: list endpoints < 200ms with 10k clients
and 50k opportunities; CSV export of 50k opportunities < 5s and
< 100MB memory; full test suite < 60s
**Constraints**: hand-written code (no AI), no third-party SSO,
no background jobs, single-currency
**Scale/Scope**: 1 owner, up to 50k clients and 200k opportunities
over the lifetime of v1; one host, one process, one DB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

| Principle | Status | Note |
|---|---|---|
| I. Spec-First | ✅ | Spec, plan, research, data-model, tasks all exist before code. |
| II. Hand-Written Code Only | ✅ | Constitution enforces; PR review verifies. |
| III. Money is Decimal | ✅ | `DecimalField(14, 2)` on `Oportunidad.monto`. |
| IV. Soft Delete | ✅ | `activo` on Cliente, Contacto, Oportunidad, Actividad, Etiqueta. |
| V. ORM is Sacred | ✅ | `assertNumQueries` tests for every list/detail view. |
| VI. Validation at the Right Layer | ✅ | DB integrity in models, field rules in `validate_<field>`, cross-field in `validate`. |
| VII. No Silent Failures | ✅ | Audit log on every mutation; structured error JSON on every failure. |
| VIII. Tests at the API Boundary | ✅ | pytest-django `APIClient` for every endpoint; integration over unit. |

No violations. No need to fill the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/001-crm-mvp/
├── spec.md              # This is the spec
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Tech stack and tradeoffs
├── data-model.md        # Entities, fields, decisions
├── quickstart.md        # How to get the system running
├── tasks.md             # Phase 2 output (/speckit.tasks)
└── contracts/
    └── api.yaml         # OpenAPI 3 spec of the API surface
```

### Source Code (repository root)

```text
.
├── config/                      # Django project (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                        # shared infrastructure
│   ├── models.py                # abstract: TimeStampedModel, SoftDeleteModel, AuditModel
│   ├── managers.py              # SoftDeleteManager
│   ├── api/
│   │   ├── serializers.py       # BusquedaGuardadaSerializer
│   │   ├── views.py             # BusquedaGuardadaViewSet
│   │   └── urls.py
│   ├── migrations/
│   └── tests/
├── clientes/                    # contact management: Cliente, Contacto, Etiqueta
│   ├── models.py
│   ├── managers.py
│   ├── signals.py               # audit log hooks
│   ├── admin.py
│   ├── views.py                 # vanilla Django views (HTML)
│   ├── urls.py
│   ├── forms.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py             # ViewSets
│   │   ├── filters.py           # FilterSets
│   │   ├── permissions.py
│   │   ├── renderers.py         # CSV streaming renderer
│   │   └── urls.py
│   ├── services/
│   │   └── audit.py             # diff helpers
│   ├── migrations/
│   └── tests/
├── oportunidades/               # sales pipeline: Oportunidad, Actividad
│   ├── models.py
│   ├── managers.py
│   ├── signals.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   ├── permissions.py
│   │   └── urls.py
│   ├── services/
│   │   ├── pipeline.py          # mover_etapa, ensure_default_pipeline
│   │   └── audit.py
│   ├── migrations/
│   └── tests/
├── pipeline/                    # pipeline configuration: Pipeline, Etapa
│   ├── models.py
│   ├── signals.py               # ensure single default pipeline
│   ├── admin.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── migrations/
│   └── tests/
├── audit/                       # audit trail: AuditLog
│   ├── models.py
│   ├── admin.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── urls.py
│   ├── migrations/
│   └── tests/
├── dashboard/                   # analytics: no models, read-only endpoint
│   ├── views.py
│   ├── services.py              # aggregations
│   ├── api/
│   │   └── urls.py
│   ├── urls.py
│   └── tests/
├── templates/
│   ├── base.html
│   ├── registration/
│   │   ├── login.html
│   │   └── logged_out.html
│   └── clientes/
│       ├── cliente_list.html
│       ├── cliente_detail.html
│       └── cliente_form.html
├── conftest.py                  # project-wide pytest fixtures (api_client, authenticated_client)
├── seed.py                      # Faker-based seeder
├── manage.py
├── pyproject.toml
├── requirements.txt
└── .specify/                    # spec-kit configuration
```

**Structure Decision**: Six Django apps (`core`, `clientes`,
`oportunidades`, `pipeline`, `audit`, `dashboard`) inside one
project, organized by bounded context. See `adr-001-bounded-context-apps.md`
for the full rationale. The split follows domain boundaries that
are obvious to the user: shared infra (`core`), contacts
(`clientes`), sales pipeline (`oportunidades`), pipeline config
(`pipeline`), audit trail (`audit`), and analytics (`dashboard`).
Cross-app FKs are explicit. Each app has its own `api/`,
`services/`, and `tests/` subfolder.

## Migration strategy

Migrations are run in this order:

1. `clientes.0001_initial` — Cliente, Contacto, Actividad, Etiqueta.
2. `pipeline.0001_initial` — Pipeline, Etapa.
3. `clientes.0002_oportunidad` — Oportunidad with FK to Cliente and Etapa.
4. `audit.0001_initial` — AuditLog.
5. `clientes.0003_seed_default_pipeline` — data migration that calls
   `ensure_default_pipeline` to create the 4-stage default.

A single `migrate` from clean state takes < 2 seconds.

## API contract

The API surface is documented in `contracts/api.yaml` (OpenAPI 3).
The `APIClient` tests in `clientes/tests/test_api_*.py` assert the
shape of every endpoint. The OpenAPI is generated by hand (no
spectacular in v1) to keep dependencies low.

## Endpoint surface

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/auth/me/` | Current user info |
| POST | `/api/auth/login/` | Session login |
| POST | `/api/auth/logout/` | Session logout |
| GET, POST | `/api/clientes/` | List, create |
| GET, PATCH, DELETE | `/api/clientes/<id>/` | Detail, update, archive |
| GET, POST | `/api/clientes/<id>/contactos/` | Contacts nested |
| GET, POST | `/api/oportunidades/` | List, create |
| GET, PATCH, DELETE | `/api/oportunidades/<id>/` | Detail, update, archive |
| POST | `/api/oportunidades/<id>/mover_etapa/` | Move to a new stage |
| GET, POST | `/api/actividades/` | List, create |
| GET, PATCH, DELETE | `/api/actividades/<id>/` | Detail, update, archive |
| GET, POST | `/api/etiquetas/` | List, create |
| GET, PATCH, DELETE | `/api/etiquetas/<id>/` | Detail, update, archive |
| GET, POST | `/api/etiquetas/<id>/clientes/` | Tag a client |
| GET, POST | `/api/pipelines/` | List, create |
| GET | `/api/pipelines/default/` | The default pipeline |
| GET, POST | `/api/etapas/` | List, create |
| GET, POST | `/api/audit/` | Audit log list |
| GET | `/api/audit/?model=Cliente&object_id=<id>` | Object history |
| GET | `/api/dashboard/` | Dashboard metrics |
| GET | `/api/busquedas_guardadas/` | Saved searches |
| POST | `/api/busquedas_guardadas/` | Create a saved search |
| GET, DELETE | `/api/busquedas_guardadas/<id>/` | Detail, delete |
| POST | `/api/busquedas_guardadas/<id>/ejecutar/` | Run a saved search |

All list endpoints accept `?format=csv` for streaming CSV export.

## Authentication flow

1. Owner visits `/api/clientes/`.
2. Server returns 403 with a `Location: /api/auth/login/`.
3. Owner posts credentials to `/api/auth/login/`.
4. Server sets the session cookie and returns 200.
5. Owner retries `/api/clientes/`, gets 200 with the list.

For DRF API clients (browsable, tests), 403 with the session cookie
absent. For curl clients, 401 with a hint.

## Performance strategy

- All list queries use `select_related` for FK and `prefetch_related`
  for reverse FK and M2M.
- All list views are paginated (default 25 per page).
- All list views that support CSV use `StreamingHttpResponse` with
  an `iterator()` queryset.
- Aggregation queries for the dashboard run in a single query each
  (no Python-side loops).
- `Cliente.ciudad` is indexed. `AuditLog.timestamp` is indexed.
  Other indexes are added only when a measured query needs them.

## Risk register

- **R-1 (medium)**: Audit log diff on `update` requires the loaded
  state. If the model is updated without a `from_db` snapshot, the
  diff is wrong. Mitigation: the `_loaded_values` check is in
  `clientes/services/audit.py:compute_diff`, with a fallback to a
  re-fetch and an explicit log warning.
- **R-2 (low)**: CSV streaming for very large querysets still loads
  the queryset into a generator. For 1M rows the generator is cheap
  but the network is the bottleneck. Mitigation: server-side
  pagination is documented as the recommended pattern for huge
  exports.
- **R-3 (low)**: Soft delete via manager means a model FK to a
  soft-deleted row can still resolve. The default manager hides the
  archived rows, but explicit `objects_all.filter(...)` queries
  show them. This is intentional, not a bug. Documented in
  `data-model.md`.

## Out of scope (deferred)

The following are explicit non-goals for v1:

- Multi-tenant / multi-org support
- Multi-currency
- Email integration (IMAP/SMTP)
- Calendar integration
- File uploads / attachments
- Realtime updates (websockets)
- Mobile-optimized UI
- Internationalization (i18n) beyond hardcoded Spanish
- Background jobs
- A public API (the API is owner-only, session-auth)
- Webhooks / event subscriptions

Each of these is a candidate for v2. The constitution will be
amended before any of them lands.
