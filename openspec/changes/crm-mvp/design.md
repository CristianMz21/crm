# Design — CRM MVP

The HOW behind the spec. Architecture, data model, ORM patterns, validation
rules, signal design, testing strategy, and the key tradeoffs that justify
the choices.

---

## 1. Architecture

Seven layers, one per day of the plan. They stack, not replace.

```
┌─────────────────────────────────────────────────────────────┐
│  Capa 7 — Cliente (templates, AJAX) — fuera de scope       │
├─────────────────────────────────────────────────────────────┤
│  Capa 6 — Signals (efectos transversales)        → day 6    │
├─────────────────────────────────────────────────────────────┤
│  Capa 5 — Managers / QuerySets custom            → day 6    │
├─────────────────────────────────────────────────────────────┤
│  Capa 4 — API REST (DRF)                          → day 4    │
├─────────────────────────────────────────────────────────────┤
│  Capa 3 — ORM (queries, N+1)                      → day 5    │
├─────────────────────────────────────────────────────────────┤
│  Capa 2 — Vistas vanilla + URLs + templates       → day 2    │
├─────────────────────────────────────────────────────────────┤
│  Capa 1 — Modelos + admin + migraciones           → day 1    │
└─────────────────────────────────────────────────────────────┘
```

Layers 1-3 are the data and query layer. Layers 4-6 expose the data through
HTTP and add cross-cutting concerns. Layer 7 is the human-facing client;
this project stops at the Browsable API of DRF.

### Folder layout

```
crm/
├── manage.py
├── requirements.txt
├── pyproject.toml
├── seed.py
├── config/                  # proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── clientes/                # app única
│   ├── models.py
│   ├── managers.py          # day 6
│   ├── signals.py           # day 6
│   ├── views.py             # day 2
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   ├── api/                 # day 4
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── urls.py
│   ├── migrations/
│   └── tests/
│       ├── conftest.py
│       ├── test_models.py
│       ├── test_orm.py
│       ├── test_api.py
│       └── test_signals.py
├── templates/clientes/
├── openspec/                # este change
└── docs/                    # NO. La doc vive en openspec/
```

---

## 2. Data model

Five entities. ASCII for the relationship graph:

```
                ┌─────────────┐
                │  Etiqueta   │
                └──────┬──────┘
                       │  M2M
                       │
┌──────────┐        ┌───┴────┐         ┌──────────────┐
│ Contacto │◄───────┤Cliente ├────────►│ Oportunidad  │
│   (FK)   │ 1    N │  (1)   │ 1     N │   (FK)       │
└──────────┘        └───┬────┘         └──────────────┘
                       │ 1
                       │ N
                  ┌────┴──────┐
                  │ Actividad │
                  │   (FK)    │
                  └───────────┘
```

### Decisions per field

| Field | Decision | Rationale |
|---|---|---|
| `Cliente.email` | `unique=True` | Contacto principal, debe ser único en toda la tabla. |
| `Cliente.activo` | `BooleanField(default=True)` | Soft delete para mantener histórico de oportunidades. |
| `Cliente.ciudad` | `db_index=True` | Filtros de la API lo usan. |
| `Contacto.cliente` | `on_delete=CASCADE` | Un contacto huérfano no tiene sentido comercial. |
| `Oportunidad.monto` | `DecimalField(12, 2)` | Dinero. Float introduce drift. |
| `Oportunidad.estado` | `CharField(choices=...)` | Cuatro valores fijos; no amerita tabla aparte. |
| `Oportunidad.fecha_cierre` | `null=True, blank=True` | Solo se llena cuando se cierra. |
| `Actividad.tipo` | `CharField(choices=...)` | Tres valores: llamada, email, reunion. |
| `Etiqueta.nombre` | `unique=True, max_length=50` | Tags cortos, sin duplicados. |

`Meta.ordering` is set on each model so default querysets are deterministic:
`Cliente` by nombre, `Contacto` by `cliente, nombre`, `Oportunidad` by
`-fecha_creacion`.

---

## 3. ORM patterns

The most exam-relevant section. Everything here is implemented by hand
during day 5.

### select_related vs prefetch_related

| Relationship kind | Use | Reason |
|---|---|---|
| ForeignKey (1-to-1 result row) | `select_related` | SQL JOIN, one row. |
| OneToOneField | `select_related` | Same as FK. |
| Reverse ForeignKey (1-to-N) | `prefetch_related` | One query per relation, joined in Python. |
| ManyToMany (N-to-N) | `prefetch_related` | Same. |

> **Rule:** if the related side returns a single object → `select_related`.
> If it returns many → `prefetch_related`.

### The N+1 problem

Pattern without optimization:

```python
clientes = Cliente.objects.all()
for c in clientes:
    print(c.contactos.count())  # 1 query per cliente
```

N+1 queries: 1 to fetch the queryset + N to fetch each relation.

The day 5 task locks the fix with `assertNumQueries`:

```python
def test_detalle_cliente_no_hace_n_mas_1(cliente_con_relaciones):
    with CaptureQueriesContext(connection) as ctx:
        cliente = (
            Cliente.objects
            .prefetch_related("contactos", "oportunidades", "actividades", "etiquetas")
            .get(pk=cliente_con_relaciones.pk)
        )
        list(cliente.contactos.all())
        list(cliente.oportunidades.all())
        list(cliente.actividades.all())
        cliente.etiquetas.all()  # .exists() inside prefetch doesn't trigger extra
    assert len(ctx.captured_queries) <= 5
```

### Aggregations

```python
Oportunidad.objects.filter(estado="ganado").aggregate(total=Sum("monto"))
Oportunidad.objects.values("estado").annotate(
    promedio=Avg("monto"), cantidad=Count("id")
)
```

`aggregate` returns a single dict. `annotate` adds a field per row.

### Q objects for OR

```python
Cliente.objects.filter(
    Q(activo=True, ciudad="Cali") | Q(oportunidades__estado="ganado")
).distinct()
```

Always `.distinct()` when joining reverse relations and OR-ing, or the result
will have duplicates.

### `bulk_create` in the seed

`bulk_create` is used in `seed.py` to insert thousands of rows in a single
statement. Tradeoffs:

- ✅ Fast.
- ❌ Does NOT fire signals.
- ❌ Does NOT refresh `pk` on the instance until after the bulk insert.

For the seed this is fine: no signal depends on the seed, and we re-read
from the DB after `bulk_create` when we need pks.

---

## 4. API design

DRF only. No DRF auth in this project (out of scope).

### Endpoints

| Method | Path | ViewSet action | Notes |
|---|---|---|---|
| GET | `/api/clientes/` | list | paginated, filterable |
| POST | `/api/clientes/` | create | validated |
| GET | `/api/clientes/<pk>/` | retrieve | nested contactos |
| PUT/PATCH | `/api/clientes/<pk>/` | update | — |
| DELETE | `/api/clientes/<pk>/` | destroy | cascades to contactos |
| GET | `/api/contactos/` | list | — |
| GET/POST | `/api/oportunidades/` | list/create | validated |

All routes come from a single `DefaultRouter` registered in
`clientes/api/urls.py`, included at `/api/` in `config/urls.py`.

### Validation: three levels

| Level | Method | Use case | Example |
|---|---|---|---|
| Field | `validate_<field>(self, value)` | Format, forbidden domain | Reject `*@test.com` |
| Object | `validate(self, attrs)` | Cross-field rule | `estado=ganado` requires `fecha_cierre` |
| Meta | `validators=[...]` | Reuse Django validators | `MinValueValidator(0)` |

The `ganado` rule is implemented in the `OportunidadSerializer.validate`,
not in the model `clean()`. The model `clean()` is not invoked by DRF by
default, and the rule is a business rule (skip-able in data migrations),
not a database integrity constraint.

### Pagination

Global in `settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

### Filtering

Filter by `?ciudad=...&activo=true` via the `get_queryset` override on the
viewset. Day 4 keeps it manual; switching to `django-filter.FilterSet` is
out of scope for this change.

---

## 5. Custom manager

In `clientes/managers.py`:

```python
class ClienteQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(activo=True)

    def con_oportunidades_ganadas(self):
        return self.filter(oportunidades__estado="ganado").distinct()
```

Wired up in the model:

```python
class Cliente(models.Model):
    ...
    objects = ClienteManager.from_queryset(ClienteQuerySet)()
```

Usage:

```python
Cliente.activos.all()
Cliente.con_oportunidades_ganadas().filter(ciudad="Cali")
```

Encadenable because it lives on the queryset, not the manager.

---

## 6. Signal

One signal, in `clientes/signals.py`:

- **Trigger:** `post_save` of `Oportunidad`.
- **Condition:** `instance.estado == "ganado"`.
- **Effect:** ensure one `Actividad` of `tipo="llamada"` exists for the
  Cliente, with nota referencing the Oportunidad titulo.
- **Registered in:** `clientes/apps.py:ready()`.

### Why this signal is correct (and most aren't)

1. **Effect is cross-cutting** — happens from admin, API, scripts. A single
   trigger point beats repeating the logic in N places.
2. **Idempotent** — checks if the actividad already exists before creating.
   The same opportunity can be saved multiple times in a session.
3. **Covers both create and update** — listens on `post_save`, not
   `post_create`. If a deal moves from `en_proceso` to `ganado`, the
   actividad still gets created.
4. **No raw-save side effects** — checks `instance.estado` after the save.
   For `loaddata` with `_raw=True` it still fires; that's acceptable for
   this project because we don't ship fixture data with `ganado` deals.

The signal is **not** registered from `models.py` (that causes
`AppRegistryNotReady`). It is imported in `apps.py:ready()`.

---

## 7. Testing

- Framework: `pytest` + `pytest-django`. Configured in `pyproject.toml`.
- Fixtures in `clientes/tests/conftest.py`: `cliente`, `cliente_con_contactos`,
  `oportunidad_ganada`, `api_client`.
- Database: `pytest-django` creates and destroys a test DB per session.
- The `assertNumQueries` test in `test_orm.py` is the regression guard
  for the day 5 N+1 fix.

Coverage target: 100% of the spec scenarios are exercised. The
verify-report.md maps each scenario to a test or marks it untested
with reason.

---

## 8. Key tradeoffs and decisions

### D-1: Soft delete via `activo` vs hard delete

**Chose:** `activo` flag.

Soft delete keeps historical reports working and is simple. Cost: every
queryset that should only show active records must filter explicitly.
Mitigated by the `Cliente.activos()` manager method.

### D-2: Validation in serializer, not in model

**Chose:** `validate()` in the serializer, not `clean()` in the model.

`clean()` is not invoked by `save()` or by DRF. Putting cross-field
validation there means it would not fire on the most common write paths.
Putting it in the serializer gives a JSON error in the format DRF
expects, and it still applies when the same model is exposed via other
DRF endpoints in the future.

### D-3: SQLite for the project

**Chose:** SQLite. The default.

The project is local, runs in 90 minutes, has no concurrency story. Adding
Postgres adds setup cost and a service dependency for no benefit at this
scale. If the project ever ships to a shared environment, switching is a
`settings.py` change.

### D-4: One app, not many

**Chose:** one app `clientes`. Five related entities do not justify
splitting into bounded contexts at this size. If `clientes/models.py`
grows past ~300 lines, split is a standard refactor.

### D-5: `bulk_create` in the seed

**Chose:** `bulk_create` in `seed.py`, not `create()` in a loop.

Speed (one INSERT vs thousands) and clarity. No signal in this project
depends on the seed, so the no-signals trade-off is acceptable.

### D-6: No DRF auth, no permissions

**Chose:** `AllowAny` everywhere in this project.

This is a training project running locally. Adding auth adds a
non-trivial chunk of code that is not the focus of the exercise. In
production this would be `IsAuthenticated` (or similar) by default.

---

## 9. Pitfalls (things to keep an eye on)

Curated from real Django mistakes that show up in code review. Each
links back to a spec requirement or a section of this design.

| Pitfall | Where it bites | What we do |
|---|---|---|
| N+1 on detail views | Day 5 | `prefetch_related` everywhere; `assertNumQueries` test. |
| `FloatField` for money | Day 3 | `DecimalField`. |
| `clean()` in model, expected to fire from API | Day 4 | Validation in serializer. |
| `bulk_create` not firing signals | Day 3 seed | Document and accept. |
| Hardcoded `pk=1` in tests | Day 6 | Fixtures with explicit `cliente.pk`. |
| `on_delete` not specified | Day 1 | Always explicit. |
| Signal registered in `models.py` (causes `AppRegistryNotReady`) | Day 6 | Registered in `apps.py:ready()`. |
| `bulk_create` instances with `pk=None` after insert | Day 3 seed | Re-read from DB or pre-generate UUIDs. |
| `auto_now` vs `auto_now_add` confusion | Day 1 | `auto_now_add=True` for `fecha_creacion`. |
| Forgetting `.distinct()` on reverse-relation ORs | Day 5 | Always `.distinct()` on those queries. |

---

## 10. File map

The day-to-day mapping from spec to file:

| Spec requirement | File(s) |
|---|---|
| R-MODELS-01..05 | `clientes/models.py`, `clientes/migrations/0001_initial.py` |
| R-VIEWS-01..03 | `clientes/views.py`, `clientes/urls.py`, `config/urls.py`, `templates/clientes/*.html` |
| R-API-01..04 | `clientes/api/serializers.py`, `clientes/api/views.py`, `clientes/api/urls.py`, `clientes/api/filters.py`, `config/settings.py` (REST_FRAMEWORK) |
| R-SEED-01 | `seed.py` |
| R-ORM-01..03 | `clientes/views.py` (detail view), `clientes/tests/test_orm.py` |
| R-MGR-01..02 | `clientes/managers.py`, `clientes/models.py` |
| R-SIG-01 | `clientes/signals.py`, `clientes/apps.py`, `clientes/tests/test_signals.py` |
| R-TEST-01..04 | `clientes/tests/test_models.py`, `clientes/tests/test_api.py` |
| R-VERIFY-01 | `openspec/changes/crm-mvp/verify-report.md` |
