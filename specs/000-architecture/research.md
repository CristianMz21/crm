# Research: CRM MVP

> The "why" behind the technology choices. Captures the alternatives
> considered, the tradeoffs, and the rationale.

## Tech stack

| Layer | Choice | Version | Why |
|---|---|---|---|
| Language | Python | 3.13 | Latest stable, performance improvements, modern typing. |
| Web framework | Django | 6.0 | Mature ORM, batteries-included, perfect for CRMs. |
| API | Django REST Framework | 3.17 | The de-facto Django REST layer. Excellent serializer validation. |
| Filtering | django-filter | 24+ | Declarative FilterSet, integrates with DRF cleanly. |
| Auth | Django built-in | — | Sufficient for single-user v1. No third-party SSO. |
| Database | SQLite (dev + tests) | — | Zero-config, fast tests, AGPL allows. Postgres in production is a config switch. |
| Testing | pytest + pytest-django | 8+ | Concise fixtures, faster than unittest, better output. |
| Data generation | Faker | 25+ | Realistic seed data, supports es_ES locale. |
| CSV export | StreamingHttpResponse + Python csv | stdlib | No third-party dep needed; streams for large sets. |
| Background jobs | None in v1 | — | All operations are synchronous in v1. django-q or celery is a future change. |

## Alternatives considered

### Why Django and not Flask / FastAPI?

The project is an exercise in Django + DRF muscle memory. Django
gives us:
- A battle-tested ORM.
- A built-in admin.
- A built-in auth.
- Built-in migrations.

Flask would force us to assemble all of this. FastAPI would give us
async and OpenAPI generation for free but no admin, no ORM that
matches Django's, and a different mindset. The choice is Django.

### Why DRF and not Django Ninja or FastAPI?

DRF is the standard. Django Ninja is faster and gives OpenAPI for
free, but the project goal is to recover the Django + DRF muscle
memory, not to learn a new framework. We stay with DRF.

### Why pytest, not unittest?

`pytest` fixtures are cleaner. `assertNumQueries` works with
`pytest-django`. The output on failure is more readable. The
tradeoff is one extra dependency (`pytest-django`).

### Why SQLite and not Postgres?

In v1, the CRM is a single-host single-user tool. SQLite handles
that with no setup. Postgres is a future move when the owner
deploys the CRM on a real server with multiple workers. The
project's data layer does not depend on SQLite-specific behavior
(uses no JSONField-only-in-SQLite features, no
`select_for_update(skip_locked=True)`).

### Why no Celery in v1?

All operations in v1 are synchronous: API request → DB write →
response. There are no scheduled jobs, no email sends, no heavy
background work. Adding Celery would add Redis, a worker process,
and a failure mode (jobs that don't run). The constitution says
"start simple, YAGNI". We add it when the first background need
appears.

### Why django-filter, not manual `get_queryset` overrides?

The filter surface is large (`?ciudad=`, `?activo=`, `?search=`,
`?monto__gte=`, `?monto__lte=`, `?asignado_a=`, `?etapa=`).
django-filter centralizes the filter declarations in a `FilterSet`
class and the wiring in `filter_backends = [DjangoFilterBackend]`.
Manual `get_queryset` overrides get messy and error-prone fast.

### Why streaming CSV with stdlib, not `django-import-export`?

`django-import-export` is a great tool, but for one-way export
(CSV out, no import in v1) it is overkill. The streaming
implementation is ~30 lines and uses the standard library. We pull
in `django-import-export` only when import lands.

### Why `select_related` / `prefetch_related` over `django-auto-all` or similar?

Automatic prefetch tools hide the N+1. The constitution requires
explicit, tested optimization (`assertNumQueries`). The owner must
be able to look at a view and see the prefetch. We do it by hand
and lock it with a test.

## Patterns adopted

### `objects` filters active, `objects_all` returns everything

```python
class ClienteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

class Cliente(models.Model):
    ...
    objects = ClienteManager()
    objects_all = models.Manager()
```

### Audit log via signal, diff computed on `update`

```python
@receiver(post_save, sender=Cliente)
def audit_cliente(sender, instance, created, raw, **kwargs):
    if raw or getattr(instance, "_skip_audit", False):
        return
    if created:
        AuditLog.objects.create(
            actor=instance._audit_actor,
            action="create",
            model="clientes.Cliente",
            object_id=instance.pk,
            object_repr=str(instance),
            changes={"new": model_to_dict(instance)},
        )
    else:
        diff = compute_diff(instance)
        if diff:
            AuditLog.objects.create(
                actor=instance._audit_actor,
                action="update",
                ...
            )
```

The diff uses `instance._loaded_values` if available (Django
populates it on a load from the DB), falling back to fetching the
previous state from the DB on demand.

### Pipeline stages are seeded in a data migration

The default pipeline is created in a data migration, not in a
signal. This way the pipeline is in place before any view tries to
read it, and `createsuperuser` works without depending on the seed
data running first.

### Auth via DRF session auth + CSRF, single permission class

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

HTML clients get a redirect to the login page; DRF clients get a
403 with a `WWW-Authenticate` hint. No JWT, no tokens. The session
cookie is enough for a single-host app.

## Tradeoffs accepted

- **No background jobs in v1.** Synchronous is fine for the
  scale. When the first user complains "the dashboard is slow
  because it computes aggregations on every request", we add
  `django-q` or move to Postgres materialized views.
- **No multi-currency.** The owner is one person, one currency. If
  multi-currency is needed, the `monto` becomes a `Money` value
  object and the dashboard math gets a currency filter.
- **No realtime updates.** The owner refreshes to see new data.
  Adding websockets would mean channels, redis, and complexity. Not
  in v1.
- **Single user in practice.** The data model supports multiple
  users (so `asignado_a` makes sense), but there is no user
  management UI. The owner is the only user, created via
  `createsuperuser`.
- **No real-time collaboration.** Two users editing the same
  client at the same time last-writer-wins. Optimistic locking via
  `updated_at` is a v2 concern.
