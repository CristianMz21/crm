# Data Model: CRM MVP

> Source of truth for the entities, fields, relationships, and
> data-layer decisions. Updated whenever a model changes.

## Entity-Relationship Diagram

```
                          ┌─────────────┐
                          │   User      │  (Django auth.User)
                          └──────┬──────┘
                                 │ assigned_to
                                 │
┌─────────────┐         ┌────────▼───────────┐         ┌──────────────┐
│  Etiqueta   │◄──M2M──►│     Cliente        │◄──FK─────│  Oportunidad │
└─────────────┘         │                    │  1     N │              │
                        └────────┬───────────┘          └──────┬───────┘
                                 │ 1                          │ 1
                                 │ N                          │ N
                        ┌────────▼─────┐               ┌──────▼───────┐
                        │  Contacto    │               │  Actividad   │
                        │  (FK)        │               │  (FK)        │
                        └──────────────┘               └──────────────┘
                                                          ▲
                                                          │ N (optional)
                                                          │
                                                     Oportunidad

┌─────────────┐         ┌──────────────────┐         ┌───────────────┐
│  Pipeline   │◄──1:N──►│      Etapa       │         │   AuditLog    │
└─────────────┘         │ (orden, cerrada) │         │ (actor,model, │
                        └──────────────────┘         │  action,delta)│
                                                     └───────────────┘
```

## Entities

### `auth.User` (Django built-in)

The system uses the built-in Django User. The owner is the first
user created via `createsuperuser`. In v1, the system is
single-user; the data model allows multiple users so that the
assignment feature works.

### `clientes.Cliente`

| Field | Type | Notes |
|---|---|---|
| `nombre` | `CharField(150)` | Required |
| `email` | `EmailField(unique=True)` | Required, unique |
| `telefono` | `CharField(20, blank=True)` | Optional |
| `empresa` | `CharField(150, blank=True)` | Optional |
| `ciudad` | `CharField(100, blank=True, db_index=True)` | Optional, indexed for filters |
| `pais` | `CharField(80, blank=True, default="")` | Optional |
| `sitio_web` | `URLField(blank=True)` | Optional |
| `notas` | `TextField(blank=True)` | Optional |
| `activo` | `BooleanField(default=True)` | Soft delete flag |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | Set once |
| `fecha_modificacion` | `DateTimeField(auto_now=True)` | Updated on every save |
| `creado_por` | `ForeignKey(User, on_delete=PROTECT, related_name="+")` | Audit |
| `etiquetas` | `ManyToManyField(Etiqueta, related_name="clientes", blank=True)` | Tags |

`Meta.ordering = ["nombre"]`. Default manager `objects` returns
only `activo=True`; `objects_all` returns everything. Str is the
nombre.

### `clientes.Contacto`

| Field | Type | Notes |
|---|---|---|
| `cliente` | `ForeignKey(Cliente, on_delete=CASCADE, related_name="contactos")` | Cascade |
| `nombre` | `CharField(150)` | Required |
| `cargo` | `CharField(100, blank=True)` | Optional |
| `email` | `EmailField(blank=True)` | Optional |
| `telefono` | `CharField(20, blank=True)` | Optional |
| `notas` | `TextField(blank=True)` | Optional |
| `activo` | `BooleanField(default=True)` | Soft delete |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | |
| `creado_por` | `ForeignKey(User, on_delete=PROTECT, related_name="+")` | Audit |

`Meta.ordering = ["cliente", "nombre"]`.

### `pipeline.Pipeline`

| Field | Type | Notes |
|---|---|---|
| `nombre` | `CharField(100, unique=True)` | Required |
| `descripcion` | `TextField(blank=True)` | |
| `es_default` | `BooleanField(default=False)` | The one default pipeline |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | |

Exactly one pipeline must have `es_default=True`. A signal
enforces this.

### `pipeline.Etapa`

| Field | Type | Notes |
|---|---|---|
| `pipeline` | `ForeignKey(Pipeline, on_delete=CASCADE, related_name="etapas")` | |
| `nombre` | `CharField(50)` | "Nuevo", "En proceso", etc. |
| `orden` | `PositiveIntegerField()` | Position in the pipeline |
| `cerrada` | `BooleanField(default=False)` | True for Ganado and Perdido |
| `es_ganado` | `BooleanField(default=False)` | True for Ganado only |
| `color` | `CharField(7, blank=True, default="")` | UI hint, hex like `#ff0000` |

`Meta.ordering = ["pipeline", "orden"]`. The unique constraint
`(pipeline, orden)` is at the DB level.

### `clientes.Oportunidad`

| Field | Type | Notes |
|---|---|---|
| `cliente` | `ForeignKey(Cliente, on_delete=PROTECT, related_name="oportunidades")` | PROTECT, not CASCADE |
| `titulo` | `CharField(200)` | Required |
| `descripcion` | `TextField(blank=True)` | |
| `monto` | `DecimalField(max_digits=14, decimal_places=2)` | Required |
| `etapa` | `ForeignKey(Etapa, on_delete=PROTECT, related_name="+")` | PROTECT, stages don't disappear |
| `asignado_a` | `ForeignKey(User, on_delete=PROTECT, related_name="oportunidades", null=True, blank=True)` | Optional |
| `fecha_cierre` | `DateField(null=True, blank=True)` | Auto-set on stage=Ganado or Perdido |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | |
| `fecha_modificacion` | `DateTimeField(auto_now=True)` | |
| `creado_por` | `ForeignKey(User, on_delete=PROTECT, related_name="+")` | |

`Meta.ordering = ["-fecha_creacion"]`. Index on `(etapa, activo)`
(implicit via FK on etapa).

### `clientes.Actividad`

| Field | Type | Notes |
|---|---|---|
| `cliente` | `ForeignKey(Cliente, on_delete=CASCADE, related_name="actividades")` | Cascade |
| `oportunidad` | `ForeignKey(Oportunidad, on_delete=SET_NULL, null=True, blank=True, related_name="actividades")` | Optional |
| `tipo` | `CharField(choices=TIPO_CHOICES)` | llamada, email, reunion |
| `nota` | `TextField()` | Required |
| `fecha` | `DateTimeField(auto_now_add=True)` | |
| `creado_por` | `ForeignKey(User, on_delete=PROTECT, related_name="+")` | |

`Meta.ordering = ["-fecha"]`.

### `clientes.Etiqueta`

| Field | Type | Notes |
|---|---|---|
| `nombre` | `CharField(50, unique=True)` | Required |
| `color` | `CharField(7, blank=True, default="")` | |
| `descripcion` | `CharField(200, blank=True)` | |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | |

M2M with Cliente via `cliente.etiquetas`.

### `audit.AuditLog`

| Field | Type | Notes |
|---|---|---|
| `actor` | `ForeignKey(User, on_delete=PROTECT, related_name="+", null=True)` | User, nullable for system actions |
| `action` | `CharField(choices=ACTION_CHOICES)` | create, update, delete |
| `model` | `CharField(80)` | App label + model name, e.g. `clientes.Cliente` |
| `object_id` | `PositiveBigIntegerField()` | The pk |
| `object_repr` | `CharField(255)` | `str(obj)` at the time of the action |
| `changes` | `JSONField()` | Old/new diff, see below |
| `timestamp` | `DateTimeField(auto_now_add=True, db_index=True)` | Indexed for time-range queries |

`Meta.indexes = [Index(fields=["model", "object_id"]),
Index(fields=["timestamp"])]`. `Meta.ordering = ["-timestamp"]`.

The `changes` JSON structure:

```json
{
  "field_name": {"old": <previous>, "new": <current>},
  ...
}
```

For `create` actions, only `"new"` is present (no `old`).
For `delete` actions, only `"old"` is present (no `new`).
For `update` actions, both are present, but only for changed
fields.

### `clientes.BusquedaGuardada`

| Field | Type | Notes |
|---|---|---|
| `nombre` | `CharField(100)` | Required |
| `endpoint` | `CharField(100)` | e.g. `clientes`, `oportunidades` |
| `filtros` | `JSONField()` | The query params as a dict |
| `creado_por` | `ForeignKey(User, on_delete=CASCADE, related_name="busquedas_guardadas")` | |
| `fecha_creacion` | `DateTimeField(auto_now_add=True)` | |

`Meta.unique_together = [("endpoint", "nombre", "creado_por")]`.

## Decisions

### D-1: `on_delete=PROTECT` on the business FKs of Oportunidad

Oportunidades are the audit trail. Deleting a client or a stage
should not silently destroy them. PROTECT forces an explicit
decision. The exception is `Actividad.oportunidad`, which is
`SET_NULL` because activities are notes, and losing the link to
the opportunity is preferable to losing the note.

### D-2: DecimalField for money, never FloatField

`Oportunidad.monto` is `DecimalField(max_digits=14, decimal_places=2)`.
This is non-negotiable per the constitution. All `aggregate` calls
on `monto` return `Decimal`. The API serializes Decimal as JSON
string to preserve precision.

### D-3: Soft delete via `activo`, not a generic `is_deleted`

`activo` (active) is a positive concept that matches the user
intent: "this client is active, show it in lists". A generic
`is_deleted` requires the model to query `is_deleted=False`
everywhere. With `activo`, the default is `True` and the default
manager filters `activo=True`. The opposite mental model.

### D-4: Custom default manager returns only `activo=True`

`Cliente.objects` and `Oportunidad.objects` and others return only
non-archived records. `Cliente.objects_all` returns everything. This
is the same pattern as `django-model-utils` `SoftDeleteManager`. We
do it by hand to keep dependencies minimal.

### D-5: Audit log writes via signals

`post_save` and `post_delete` signals on the five business models
write to `AuditLog`. The signal reads `created` to distinguish
create from update. For update, it uses `instance.__class__._loaded_values`
to compute the diff (if available) or falls back to a full
snapshot.

The signal is registered in `clientes/apps.py:ready()`. The audit
log is NOT registered to itself (a write to AuditLog does not
trigger another AuditLog entry).

### D-6: `asignado_a` is optional

A user can exist without having any opportunities assigned. An
opportunity can exist without being assigned. The dashboard
includes unassigned opportunities in the totals.

### D-7: One default pipeline, enforced by a signal

The first time the system runs, a migration creates a default
pipeline with four stages (Nuevo, En proceso, Ganado, Perdido).
A pre-save signal on `Pipeline` ensures only one has
`es_default=True`.

### D-8: `fecha_cierre` is auto-managed

When an opportunity is moved to a stage with `cerrada=True`,
`fecha_cierre` is auto-set to today. When it is moved back to a
non-closed stage, `fecha_cierre` is cleared. This is enforced in
the `mover_etapa` service method, not in the model `save()`,
because the model does not know which stage is "closed".

### D-9: `db_index=True` only on real query columns

`Cliente.ciudad` is indexed because the API filters by it. The
owner does not filter by `empresa` or `pais` in v1, so those are
not indexed. `AuditLog.timestamp` is indexed because the API
queries it. `AuditLog.model + object_id` is a composite index for
the per-object history view.

## What we are NOT modeling in v1

- **Currency**: single-currency. The `monto` field is just a
  decimal. No `Currency` table.
- **Taxes / line items**: deals are a single amount. No
  `LineItem` table. If a deal needs to be broken down, the
  breakdown goes in `descripcion`.
- **Recurring revenue**: no MRR, no ARR. The `monto` is a one-time
  amount.
- **Email integration**: no `EmailAccount` table. Activities of
  type `email` are notes about emails already sent.
- **Calendar integration**: no `Event` table. Activities of type
  `reunion` are notes about meetings already held.
- **Multi-tenancy**: no `Organization` or `Team`. The data belongs
  to the User.
- **Custom fields**: no per-client custom fields. Tags cover the
  "I want to mark this client as X" use case.
- **Files / attachments**: no file uploads. Notes are plain text.
- **Localization**: hardcoded in Spanish (the owner's language).
  The `gettext_lazy` hooks are in place but no `.po` files are
  generated in v1.
