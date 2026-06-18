# Tasks: CRM MVP — Execution Plan for 6-App Architecture

> **ADR-001**: Models organized into 6 bounded-context apps.
> See `adr-001-bounded-context-apps.md` for rationale.
>
> This file replaces the previous 150-task list. It is focused,
> concrete, and ordered for the 6-app structure. Each task has
> exact file paths, spec references, and verification commands.

**Input**: Spec from `spec.md`, plan from `plan.md`, data model
from `data-model.md`, research from `research.md`, ADR-001.

**Goal**: Reach MVP = US1 (Auth) + US2 (Clientes + Contactos) +
US3 (Pipeline + Oportunidades + Dashboard).

**Rule**: Code is hand-written (constitution principle II). Tests
at the API boundary (principle VIII). N+1 is P0 (principle V).

---

## Phase 0: Core abstract models (BLOCKS everything)

> Every concrete model inherits from these. Must be first.

### S001 — `core/models.py`: TimeStampedModel

**File**: `core/models.py`
**Spec**: `data-model.md` → `core.TimeStampedModel`
**Depends on**: nothing
**What**: Abstract model with `fecha_creacion` (auto_now_add) and
`fecha_modificacion` (auto_now). `class Meta: abstract = True`.

**Verify**:
```bash
uv run python manage.py makemigrations core
# Expected: "No changes detected" (abstract models don't migrate)
uv run python manage.py shell -c "from core.models import TimeStampedModel; print(TimeStampedModel._meta.abstract)"
# Expected: True
```

- [ ] S001 Done

### S002 — `core/models.py`: SoftDeleteModel

**File**: `core/models.py`
**Spec**: `data-model.md` → `core.SoftDeleteModel`
**Depends on**: S001
**What**: Abstract model with `activo = BooleanField(default=True)`.
`class Meta: abstract = True`.

**Verify**:
```bash
uv run python manage.py shell -c "from core.models import SoftDeleteModel; print(SoftDeleteModel._meta.abstract, SoftDeleteModel._meta.get_field('activo').default)"
# Expected: True True
```

- [ ] S002 Done

### S003 — `core/models.py`: AuditModel

**File**: `core/models.py`
**Spec**: `data-model.md` → `core.AuditModel`
**Depends on**: S001
**What**: Abstract model with `creado_por = ForeignKey(User,
on_delete=PROTECT, related_name="+")`. `class Meta: abstract = True`.

**Verify**:
```bash
uv run python manage.py shell -c "from core.models import AuditModel; print(AuditModel._meta.abstract)"
# Expected: True
```

- [ ] S003 Done

### S004 — `core/managers.py`: SoftDeleteManager + SoftDeleteQuerySet

**File**: `core/managers.py`
**Spec**: `data-model.md` → D-4 (custom default manager)
**Depends on**: S002
**What**: `SoftDeleteQuerySet` with `activos()` and `archivados()`
methods. `SoftDeleteManager` extending `Manager.from_queryset(
SoftDeleteQuerySet)` that overrides `get_queryset()` to filter
`activo=True`. Also a `all_objects` manager that returns everything.

**Verify**:
```bash
uv run python manage.py shell -c "from core.managers import SoftDeleteManager; print(SoftDeleteManager)"
# Expected: <class 'core.managers.SoftDeleteManager'>
```

- [ ] S004 Done

### S005 — Checkpoint: core foundation ready

```bash
uv run python manage.py check
uv run ruff check core/
uv run ruff format --check core/
```

All three pass → core foundation is ready. Move to Phase 1.

- [ ] S005 Checkpoint passed

---

## Phase 1: Business models (BLOCKS all user stories)

> All 7 concrete models. Order matters: pipeline models first
> (because Oportunidad FKs to Etapa), then audit (because signals
> need it), then clientes (update existing), then oportunidades.

### S010 — `pipeline/models.py`: Pipeline

**File**: `pipeline/models.py`
**Spec**: `data-model.md` → `pipeline.Pipeline`
**Depends on**: S005
**What**: `Pipeline` model inheriting from `TimeStampedModel`.
Fields: `nombre` (CharField 100, unique), `descripcion` (TextField
blank), `es_default` (BooleanField default False). `__str__` returns
nombre. `Meta.ordering = ["nombre"]`.

**Verify**:
```bash
uv run python manage.py makemigrations pipeline
uv run python manage.py migrate
uv run python manage.py shell -c "from pipeline.models import Pipeline; print(Pipeline._meta.verbose_name)"
# Expected: pipeline
```

- [ ] S010 Done

### S011 — `pipeline/models.py`: Etapa

**File**: `pipeline/models.py`
**Spec**: `data-model.md` → `pipeline.Etapa`
**Depends on**: S010
**What**: `Etapa` model. Fields: `pipeline` (FK to Pipeline,
CASCADE, related_name="etapas"), `nombre` (CharField 50), `orden`
(PositiveIntegerField), `cerrada` (BooleanField default False),
`es_ganado` (BooleanField default False), `color` (CharField 7,
blank, default ""). `Meta.ordering = ["pipeline", "orden"]`.
Unique constraint on `(pipeline, orden)` via
`Meta.constraints = [UniqueConstraint(fields=["pipeline", "orden"],
name="unique_orden_per_pipeline")]`. `__str__` returns
`f"{self.pipeline.nombre} > {self.nombre}"`.

**Verify**:
```bash
uv run python manage.py makemigrations pipeline
uv run python manage.py migrate
```

- [ ] S011 Done

### S012 — `audit/models.py`: AuditLog

**File**: `audit/models.py`
**Spec**: `data-model.md` → `audit.AuditLog`
**Depends on**: S005
**What**: `AuditLog` model. Fields: `actor` (FK User, PROTECT,
null=True, related_name="+"), `action` (CharField choices:
create/update/delete), `model` (CharField 80), `object_id`
(PositiveBigIntegerField), `object_repr` (CharField 255),
`changes` (JSONField, default=dict), `timestamp`
(DateTimeField auto_now_add, db_index). `Meta.ordering =
["-timestamp"]`. Indexes on `(model, object_id)` and `timestamp`.
`__str__` returns `f"{self.action} {self.model}:{self.object_id}"`.

**Verify**:
```bash
uv run python manage.py makemigrations audit
uv run python manage.py migrate
```

- [ ] S012 Done

### S013 — `clientes/models.py`: Update Cliente

**File**: `clientes/models.py`
**Spec**: `data-model.md` → `clientes.Cliente`
**Depends on**: S004, S010 (Etiqueta has no dep, but Cliente needs
all fields)
**What**: Update the existing `Cliente` model to:
- Inherit from `TimeStampedModel`, `SoftDeleteModel`, `AuditModel`
  (from `core.models`)
- Remove the explicit `activo` and `fecha_creacion` fields (now
  inherited)
- Add: `pais` (CharField 80, blank, default ""), `sitio_web`
  (URLField blank), `notas` (TextField blank)
- Add: `etiquetas` M2M to `Etiqueta`, related_name="clientes",
  blank=True
- Replace `objects = SoftDeleteManager()` and add
  `objects_all = Manager()` (from `core.managers`)
- Keep `__str__`, `get_absolute_url`, `Meta.ordering`

**Verify**:
```bash
uv run python manage.py makemigrations clientes
uv run python manage.py migrate
uv run python manage.py shell -c "from clientes.models import Cliente; print([f.name for f in Cliente._meta.get_fields()])"
# Expected: includes 'pais', 'sitio_web', 'notas', 'etiquetas', 'fecha_modificacion', 'creado_por'
```

- [ ] S013 Done

### S014 — `clientes/models.py`: Etiqueta

**File**: `clientes/models.py`
**Spec**: `data-model.md` → `clientes.Etiqueta`
**Depends on**: S013
**What**: `Etiqueta` model inheriting from `TimeStampedModel`.
Fields: `nombre` (CharField 50, unique), `color` (CharField 7,
blank, default ""), `descripcion` (CharField 200, blank).
`__str__` returns nombre. `Meta.ordering = ["nombre"]`.

**Verify**:
```bash
uv run python manage.py makemigrations clientes
uv run python manage.py migrate
```

- [ ] S014 Done

### S015 — `clientes/models.py`: Update Contacto

**File**: `clientes/models.py`
**Spec**: `data-model.md` → `clientes.Contacto`
**Depends on**: S013
**What**: Update `Contacto` to inherit from `TimeStampedModel`,
`SoftDeleteModel`, `AuditModel`. Add: `notas` (TextField blank).
Replace `objects` with `SoftDeleteManager()`, add `objects_all`.
Keep FK to Cliente, related_name="contactos", CASCADE.

**Verify**:
```bash
uv run python manage.py makemigrations clientes
uv run python manage.py migrate
```

- [ ] S015 Done

### S016 — `oportunidades/models.py`: Oportunidad

**File**: `oportunidades/models.py`
**Spec**: `data-model.md` → `oportunidades.Oportunidad`
**Depends on**: S011 (FK to Etapa), S013 (FK to Cliente)
**What**: `Oportunidad` model inheriting from `TimeStampedModel`,
`SoftDeleteModel`, `AuditModel`. Fields: `cliente` (FK to
`clientes.Cliente`, PROTECT, related_name="oportunidades"),
`titulo` (CharField 200), `descripcion` (TextField blank),
`monto` (DecimalField max_digits=14, decimal_places=2), `etapa`
(FK to `pipeline.Etapa`, PROTECT, related_name="oportunidades"),
`asignado_a` (FK User, PROTECT, null=True, blank=True,
related_name="oportunidades"), `fecha_cierre` (DateField null=True,
blank=True). `Meta.ordering = ["-fecha_creacion"]`. `__str__`
returns titulo. Replace `objects` with `SoftDeleteManager()`.

**Verify**:
```bash
uv run python manage.py makemigrations oportunidades
uv run python manage.py migrate
uv run python manage.py shell -c "from oportunidades.models import Oportunidad; print(Oportunidad._meta.get_field('monto').__class__.__name__)"
# Expected: DecimalField
```

- [ ] S016 Done

### S017 — `oportunidades/models.py`: Actividad

**File**: `oportunidades/models.py`
**Spec**: `data-model.md` → `oportunidades.Actividad`
**Depends on**: S016
**What**: `Actividad` model inheriting from `TimeStampedModel`,
`AuditModel` (NO SoftDelete — activities are never deleted). Fields:
`cliente` (FK to `clientes.Cliente`, CASCADE, related_name=
"actividades"), `oportunidad` (FK to `oportunidades.Oportunidad`,
SET_NULL, null=True, blank=True, related_name="actividades"),
`tipo` (CharField choices: llamada/email/reunion), `nota`
(TextField). `Meta.ordering = ["-fecha"]`. `__str__` returns
`f"{self.tipo}: {self.cliente.nombre}"`.

**Verify**:
```bash
uv run python manage.py makemigrations oportunidades
uv run python manage.py migrate
```

- [ ] S017 Done

### S018 — `core/models.py`: BusquedaGuardada

**File**: `core/models.py`
**Spec**: `data-model.md` → `core.BusquedaGuardada`
**Depends on**: S005
**What**: `BusquedaGuardada` model. Fields: `nombre` (CharField
100), `endpoint` (CharField 100), `filtros` (JSONField, default=
dict), `creado_por` (FK User, CASCADE, related_name=
"busquedas_guardadas"). `Meta.unique_together = [("endpoint",
"nombre", "creado_por")]`. `__str__` returns nombre.

**Verify**:
```bash
uv run python manage.py makemigrations core
uv run python manage.py migrate
```

- [ ] S018 Done

### S019 — Checkpoint: all models ready

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
# Expected: "No changes detected" (all migrations are up to date)
uv run python manage.py migrate
uv run ruff check core/ clientes/ oportunidades/ pipeline/ audit/
uv run ruff format --check core/ clientes/ oportunidades/ pipeline/ audit/
```

All pass → all 8 models (3 abstract + 7 concrete + BusquedaGuardada)
are ready. Move to Phase 2.

- [ ] S019 Checkpoint passed

---

## Phase 2: Services, signals, admin (BLOCKS all user stories)

### S020 — `oportunidades/services/pipeline.py`: ensure_default_pipeline()

**File**: `oportunidades/services/pipeline.py`
**Spec**: `data-model.md` → D-7
**Depends on**: S019
**What**: Function `ensure_default_pipeline()` that creates a
default Pipeline (es_default=True) with 4 Etapas: Nuevo (orden=0),
En proceso (orden=1), Ganado (orden=2, cerrada=True, es_ganado=True),
Perdido (orden=3, cerrada=True). Idempotent: if a default pipeline
already exists, returns it without creating duplicates.

**Verify**:
```bash
uv run python manage.py shell -c "from oportunidades.services.pipeline import ensure_default_pipeline; p = ensure_default_pipeline(); print(p.nombre, p.etapas.count())"
# Expected: (default pipeline name) 4
```

- [ ] S020 Done

### S021 — `oportunidades/services/pipeline.py`: mover_etapa()

**File**: `oportunidades/services/pipeline.py`
**Spec**: `data-model.md` → D-8
**Depends on**: S020
**What**: Function `mover_etapa(oportunidad, etapa_id, *, actor=None)`
that: (1) sets `oportunidad.etapa_id = etapa_id`, (2) if the new
etapa has `cerrada=True`, sets `fecha_cierre = today`, (3) if the
new etapa has `cerrada=False`, clears `fecha_cierre = None`, (4)
calls `oportunidad.save()`. Raises `ValueError` if the etapa doesn't
belong to the same pipeline.

**Verify**:
```bash
uv run python manage.py shell -c "
from oportunidades.services.pipeline import ensure_default_pipeline, mover_etapa
from clientes.models import Cliente
from oportunidades.models import Oportunidad
p = ensure_default_pipeline()
etapa_ganado = p.etapas.get(es_ganado=True)
c = Cliente.objects.create(nombre='Test', email='t@t.com')
o = Oportunidad.objects.create(cliente=c, titulo='Test', monto='1000.00', etapa=p.etapas.first())
mover_etapa(o, etapa_ganado.id)
print(o.fecha_cierre is not None)
# Expected: True
"
```

- [ ] S021 Done

### S022 — `audit/services/__init__.py`: log_action()

**File**: `audit/services/__init__.py`
**Spec**: `data-model.md` → `audit.AuditLog`
**Depends on**: S012
**What**: Function `log_action(*, actor, action, instance, changes)`
that creates an `AuditLog` entry. `changes` is a dict with old/new
per field. Reads `instance.pk`, `instance.__class__._meta.label`
for the model name, `str(instance)` for object_repr.

**Verify**:
```bash
uv run python manage.py shell -c "from audit.services import log_action; print(callable(log_action))"
# Expected: True
```

- [ ] S022 Done

### S023 — `audit/services/__init__.py`: compute_diff()

**File**: `audit/services/__init__.py`
**Spec**: `data-model.md` → D-5
**Depends on**: S022
**What**: Function `compute_diff(instance)` that compares the
current instance state against the DB state (re-fetches by pk) and
returns a dict of `{field: {old: ..., new: ...}}` for changed
fields. Excludes auto-managed fields (fecha_creacion,
fecha_modificacion).

**Verify**:
```bash
uv run python manage.py shell -c "from audit.services import compute_diff; print(callable(compute_diff))"
# Expected: True
```

- [ ] S023 Done

### S024 — Signals: post_save for audit log

**File**: `clientes/signals.py`, `oportunidades/signals.py`
**Spec**: `data-model.md` → D-5
**Depends on**: S022, S023
**What**: `post_save` signal handlers for `Cliente`, `Contacto`,
`Etiqueta` (in `clientes/signals.py`) and `Oportunidad`,
`Actividad` (in `oportunidades/signals.py`). On `created=True`:
call `log_action(action="create", changes={"new": model_to_dict})`.
On `created=False`: call `compute_diff()` and if diff is non-empty,
`log_action(action="update", changes=diff)`. Skip if
`raw=True` (loaddata) or `instance._skip_audit` is True.

**Verify**:
```bash
uv run python manage.py shell -c "
from clientes.models import Cliente
from audit.models import AuditLog
c = Cliente.objects.create(nombre='AuditTest', email='audit@test.com')
log = AuditLog.objects.filter(model='clientes.Cliente', object_id=c.pk)
print(log.count(), log.first().action if log.exists() else 'none')
# Expected: 1 create
"
```

- [ ] S024 Done

### S025 — Signals: post_delete for audit log

**File**: `clientes/signals.py`, `oportunidades/signals.py`
**Spec**: `data-model.md` → D-5
**Depends on**: S024
**What**: `post_delete` signal handlers for the same 5 models. Call
`log_action(action="delete", changes={"old": model_to_dict(instance)})`.

**Verify**:
```bash
uv run python manage.py shell -c "
from clientes.models import Cliente
from audit.models import AuditLog
c = Cliente.objects.create(nombre='DeleteTest', email='del@test.com')
c.delete()  # soft delete sets activo=False, triggers post_save not post_delete
# For hard delete: c.objects_all.filter(pk=c.pk).delete()
print(AuditLog.objects.filter(model='clientes.Cliente').count())
"
```

- [ ] S025 Done

### S026 — Register signals in apps.py:ready()

**File**: `clientes/apps.py`, `oportunidades/apps.py`,
`pipeline/apps.py`
**Spec**: constitution principle VII
**Depends on**: S024, S025
**What**: In each app's `AppsConfig.ready()`, import the signals
module: `from . import signals  # noqa: F401`. Verify the AppConfig
is referenced in `INSTALLED_APPS` (either by path or by
`apps.ClientesConfig`).

**Verify**:
```bash
uv run python manage.py check
# No AppRegistryNotReady errors
```

- [ ] S026 Done

### S027 — `pipeline/signals.py`: ensure single default pipeline

**File**: `pipeline/signals.py`
**Spec**: `data-model.md` → D-7
**Depends on**: S010
**What**: `pre_save` signal on `Pipeline` that: if
`instance.es_default=True`, unset `es_default` on all other
pipelines. This ensures exactly one default at all times.

**Verify**:
```bash
uv run python manage.py shell -c "
from pipeline.models import Pipeline
Pipeline.objects.create(nombre='P1', es_default=True)
Pipeline.objects.create(nombre='P2', es_default=True)
print(Pipeline.objects.filter(es_default=True).count())
# Expected: 1 (only P2)
"
```

- [ ] S027 Done

### S028 — Data migration: seed default pipeline

**File**: `oportunidades/migrations/0002_seed_default_pipeline.py`
**Spec**: `plan.md` → Migration strategy step 5
**Depends on**: S020
**What**: Data migration that calls `ensure_default_pipeline()` in
its ` forwards` operation. `reverse` removes the seeded pipeline.

**Verify**:
```bash
uv run python manage.py migrate
uv run python manage.py shell -c "from pipeline.models import Pipeline; print(Pipeline.objects.filter(es_default=True).count())"
# Expected: 1
```

- [ ] S028 Done

### S029 — Admin registrations

**File**: `clientes/admin.py`, `oportunidades/admin.py`,
`pipeline/admin.py`, `audit/admin.py`, `core/admin.py`
**Spec**: constitution principle VII (no silent failures → admin
visibility)
**Depends on**: S019
**What**: Register every concrete model in its app's `admin.py`
with `@admin.register(Model)`. Use `list_display`, `list_filter`,
`search_fields` appropriate to each model. For `AuditLog`:
read-only (`readonly_fields = [...]`, no add/delete).

**Verify**:
```bash
uv run python manage.py check
# Start server, visit /admin/, see all models listed
```

- [ ] S029 Done

### S030 — Checkpoint: foundation ready

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py shell -c "
from core.models import TimeStampedModel, SoftDeleteModel, AuditModel, BusquedaGuardada
from clientes.models import Cliente, Contacto, Etiqueta
from oportunidades.models import Oportunidad, Actividad
from pipeline.models import Pipeline, Etapa
from audit.models import AuditLog
from oportunidades.services.pipeline import ensure_default_pipeline, mover_etapa
from audit.services import log_action, compute_diff
p = ensure_default_pipeline()
print(f'Pipeline: {p.nombre}, etapas: {p.etapas.count()}')
print('All models and services importable')
"
uv run ruff check .
uv run ruff format --check .
uv run pytest --collect-only
```

All pass → Foundation is ready. US1, US2, US3 can now begin.

- [ ] S030 Foundation checkpoint passed

---

## Phase 3: US1 — Auth (P1 MVP)

> **Goal**: Owner can log in, log out, and reach the API.
> Unauthenticated requests get 403.

### S031 — `clientes/api/views.py`: AuthViewSet

**File**: `clientes/api/views.py` (or a new `core/api/views.py`)
**Spec**: `spec.md` → US1, `contracts/api.yaml` → `/api/auth/*`
**Depends on**: S030
**What**: `AuthViewSet` with `@action` methods: `me()` returns
the current user, `login()` accepts username+password and calls
`django.contrib.auth.login()`, `logout()` calls
`django.contrib.auth.logout()`. Uses `@permission_classes([
AllowAny])` for login, default `IsAuthenticated` for the rest.

**Verify**:
```bash
uv run python manage.py shell -c "from clientes.api.views import AuthViewSet; print(AuthViewSet)"
```

- [ ] S031 Done

### S032 — `clientes/api/urls.py`: Register AuthViewSet

**File**: `clientes/api/urls.py`
**Spec**: `contracts/api.yaml` → `/api/auth/*`
**Depends on**: S031
**What**: Register `AuthViewSet` with `router.register("auth",
AuthViewSet, basename="auth")`. The `me`, `login`, `logout` actions
are custom routes.

**Verify**:
```bash
uv run python manage.py check
uv run python manage.py shell -c "
from django.urls import reverse
print(reverse('auth-me'))
"
```

- [ ] S032 Done

### S033 — Tests: test_api_auth.py

**File**: `clientes/tests/test_api_auth.py` (or `core/tests/`)
**Spec**: `spec.md` → US1 acceptance scenarios
**Depends on**: S032
**What**: Tests: (1) unauthenticated GET `/api/auth/me/` → 403,
(2) authenticated GET `/api/auth/me/` → 200 with user data,
(3) POST `/api/auth/login/` with bad credentials → 400,
(4) POST `/api/auth/login/` with good credentials → 200,
(5) POST `/api/auth/logout/` → 204.

**Verify**:
```bash
uv run pytest clientes/tests/test_api_auth.py -v
# All 5 tests pass
```

- [ ] S033 Done

### S034 — Checkpoint: US1 complete

```bash
uv run pytest -k auth -v
uv run python manage.py check
uv run ruff check .
```

All pass → US1 is done. The owner can authenticate.

- [ ] S034 US1 checkpoint passed 🎯

---

## Phase 4: US2 — Clientes + Contactos (P1 MVP)

> **Goal**: CRUD clients with search, filters, soft delete,
> nested contacts, and N+1-free queries.

### S035 — `clientes/api/serializers.py`: ContactoSerializer

**File**: `clientes/api/serializers.py`
**Spec**: `contracts/api.yaml` → `Contacto`, `ContactoCreate`
**Depends on**: S030
**What**: `ModelSerializer` for `Contacto` with fields: id, nombre,
cargo, email, telefono, notas, activo. `read_only_fields = ["id"]`.

- [ ] S035 Done

### S036 — `clientes/api/serializers.py`: ClienteSerializer + ClienteDetailSerializer

**File**: `clientes/api/serializers.py`
**Spec**: `contracts/api.yaml` → `Cliente`, `ClienteDetail`
**Depends on**: S035
**What**: `ClienteSerializer` with fields: id, nombre, email,
telefono, empresa, ciudad, pais, sitio_web, notas, activo,
fecha_creacion, fecha_modificacion, etiquetas (list of names).
`ClienteDetailSerializer` extends with nested `contactos =
ContactoSerializer(many=True, read_only=True)` and `actividades`
(read_only, from oportunidades). Add `validate_email` rejecting
`@test.com` domain.

- [ ] S036 Done

### S037 — `clientes/api/filters.py`: ClienteFilter

**File**: `clientes/api/filters.py`
**Spec**: `spec.md` → FR-011, `contracts/api.yaml` → query params
**Depends on**: S030
**What**: `FilterSet` for `Cliente` with: `ciudad` (exact),
`activo` (BooleanFilter), `search` (CharFilter, method that does
`Q(nombre__icontains) | Q(email__icontains)`).

- [ ] S037 Done

### S038 — `clientes/api/views.py`: ClienteViewSet

**File**: `clientes/api/views.py`
**Spec**: `contracts/api.yaml` → `/api/clientes/`
**Depends on**: S036, S037
**What**: `ModelViewSet` with `queryset = Cliente.objects.all()`,
`serializer_class = ClienteSerializer`, `filterset_class =
ClienteFilter`. Override `get_serializer_class()` to return
`ClienteDetailSerializer` for `retrieve`. Override `perform_destroy`
to soft-delete (`instance.activo = False; instance.save()`).

- [ ] S038 Done

### S039 — `clientes/api/views.py`: ContactoViewSet

**File**: `clientes/api/views.py`
**Spec**: `contracts/api.yaml` → `/api/clientes/{id}/contactos/`
**Depends on**: S035
**What**: `ModelViewSet` for `Contacto`. Override `get_queryset()`
to filter by `cliente_id` from the URL kwargs.

- [ ] S039 Done

### S040 — `clientes/api/urls.py`: Register viewsets

**File**: `clientes/api/urls.py`
**Depends on**: S038, S039
**What**: Register `ClienteViewSet` and `ContactoViewSet` in the
router. Add nested routes for contactos under cliente if needed.

**Verify**:
```bash
uv run python manage.py check
```

- [ ] S040 Done

### S041 — Tests: test_api_clientes.py

**File**: `clientes/tests/test_api_clientes.py`
**Spec**: `spec.md` → US2 acceptance scenarios
**Depends on**: S040
**What**: Tests for: create 201, create with bad email 400, create
with duplicate email 400, list paginated, filter by ciudad, filter
by activo, search case-insensitive, detail with nested contactos,
update, soft delete (DELETE → 204, then GET → 404), create nested
contacto, cascade on cliente delete.

- [ ] S041 Done

### S042 — Tests: test_orm.py (N+1 regression)

**File**: `clientes/tests/test_orm.py`
**Spec**: constitution principle V
**Depends on**: S040
**What**: `assertNumQueries` test for: (1) list view of clients is
bounded (constant queries regardless of N), (2) detail view of
client with contactos + actividades is at most 5 queries (1 client
+ prefetches).

- [ ] S042 Done

### S043 — Tests: test_audit.py (cliente audit)

**File**: `clientes/tests/test_audit.py` (or `audit/tests/`)
**Spec**: `spec.md` → US5 acceptance scenarios (applied to cliente)
**Depends on**: S024
**What**: Tests that create/update/delete on Cliente produce
AuditLog entries with correct action and changes.

- [ ] S043 Done

### S044 — Checkpoint: US2 complete

```bash
uv run pytest clientes/tests/ -v
uv run python manage.py check
uv run ruff check .
```

All pass → US2 is done. The owner can manage clients and contacts.

- [ ] S044 US2 checkpoint passed 🎯

---

## Phase 5: US3 — Pipeline + Oportunidades + Dashboard (P1 MVP)

> **Goal**: Create opportunities, move them through stages,
> see dashboard metrics. **This completes the MVP.**

### S045 — `pipeline/api/serializers.py`: EtapaSerializer + PipelineSerializer

**File**: `pipeline/api/serializers.py`
**Spec**: `contracts/api.yaml` → `Etapa`, `Pipeline`
**Depends on**: S030
**What**: `EtapaSerializer` (ModelSerializer for Etapa).
`PipelineSerializer` with nested `etapas = EtapaSerializer(many=True,
read_only=True)`.

- [ ] S045 Done

### S046 — `pipeline/api/views.py`: PipelineViewSet + EtapaViewSet

**File**: `pipeline/api/views.py`
**Spec**: `contracts/api.yaml` → `/api/pipelines/`
**Depends on**: S045
**What**: `PipelineViewSet` (ModelViewSet) with a `@action` `default`
that returns the default pipeline. `EtapaViewSet` (ModelViewSet).

- [ ] S046 Done

### S047 — `pipeline/api/urls.py`: Register viewsets

**File**: `pipeline/api/urls.py`
**Depends on**: S046
**What**: Register both viewsets.

- [ ] S047 Done

### S048 — `oportunidades/api/serializers.py`: OportunidadSerializer

**File**: `oportunidades/api/serializers.py`
**Spec**: `contracts/api.yaml` → `Oportunidad`, `OportunidadCreate`
**Depends on**: S030
**What**: `ModelSerializer` for `Oportunidad`. `monto` serialized as
string (DRF does this by default for DecimalField). `etapa` as
nested EtapaSerializer (read-only). Add `validate()`: if
`estado=ganado` (or etapa.cerrada and es_ganado) and no
`fecha_cierre`, raise ValidationError.

- [ ] S048 Done

### S049 — `oportunidades/api/filters.py`: OportunidadFilter

**File**: `oportunidades/api/filters.py`
**Spec**: `spec.md` → FR-011
**Depends on**: S030
**What**: `FilterSet` with: `etapa` ( FK, exact), `cliente` (FK,
exact), `asignado_a` (FK, exact), `monto__gte` (NumberFilter),
`monto__lte` (NumberFilter), `search` (CharFilter, method:
`titulo__icontains`).

- [ ] S049 Done

### S050 — `oportunidades/api/views.py`: OportunidadViewSet

**File**: `oportunidades/api/views.py`
**Spec**: `contracts/api.yaml` → `/api/oportunidades/`
**Depends on**: S048, S049, S021
**What**: `ModelViewSet` with `filterset_class = OportunidadFilter`.
Custom `@action(detail=True, methods=["post"])` `mover_etapa` that
calls `oportunidades.services.pipeline.mover_etapa(oportunidad,
etapa_id, actor=request.user)`. Override `perform_destroy` for soft
delete.

- [ ] S050 Done

### S051 — `oportunidades/api/urls.py`: Register OportunidadViewSet

**File**: `oportunidades/api/urls.py`
**Depends on**: S050
**What**: Register `OportunidadViewSet`.

- [ ] S051 Done

### S052 — `dashboard/services.py`: compute_dashboard_metrics()

**File**: `dashboard/services.py`
**Spec**: `spec.md` → US8, `contracts/api.yaml` → `Dashboard`
**Depends on**: S030
**What**: Function returning dict with: `pipeline_por_etapa` (list
of {etapa, total, cantidad} via annotate+aggregate), `ganado_mes_actual`
(Sum of monto where etapa.es_ganado and fecha_cierre this month),
`perdido_mes_actual` (same for Perdido), `win_rate` (ganado / (ganado
+ perdido)), `top_5_abiertos` (top 5 by monto where etapa.cerrada=
False).

- [ ] S052 Done

### S053 — `dashboard/api/views.py`: DashboardView

**File**: `dashboard/api/views.py`
**Spec**: `contracts/api.yaml` → `/api/dashboard/`
**Depends on**: S052
**What**: `APIView` (GET only) that calls
`compute_dashboard_metrics()` and returns the dict.

- [ ] S053 Done

### S054 — `dashboard/api/urls.py`: Register dashboard route

**File**: `dashboard/api/urls.py`
**Depends on**: S053
**What**: `path("", DashboardView.as_view(), name="dashboard")`.

- [ ] S054 Done

### S055 — Tests: test_api_oportunidades.py

**File**: `oportunidades/tests/test_api_oportunidades.py`
**Spec**: `spec.md` → US3 acceptance scenarios
**Depends on**: S051
**What**: Tests for: create 201, create without monto 400, mover to
ganado sets fecha_cierre, mover to perdido sets fecha_cierre, mover
from cerrado to abierta clears fecha_cierre, filter by etapa, filter
by monto range, filter by asignado_a, list paginated.

- [ ] S055 Done

### S056 — Tests: test_pipeline.py

**File**: `pipeline/tests/test_pipeline.py`
**Spec**: `data-model.md` → D-7
**Depends on**: S028
**What**: Tests for: `ensure_default_pipeline` creates 4 etapas,
cannot have 2 default pipelines, etapas ordered by orden.

- [ ] S056 Done

### S057 — Tests: test_dashboard.py

**File**: `dashboard/tests/test_dashboard.py`
**Spec**: `spec.md` → US8 acceptance scenarios
**Depends on**: S054
**What**: Tests for: pipeline_por_etapa, ganado_mes_actual,
perdido_mes_actual, win_rate, top_5_abiertos, empty state returns
zeros not 500.

- [ ] S057 Done

### S058 — Tests: test_orm.py for oportunidades (N+1)

**File**: `oportunidades/tests/test_orm.py`
**Spec**: constitution principle V
**Depends on**: S051
**What**: `assertNumQueries` for oportunidades list and detail.

- [ ] S058 Done

### S059 — Checkpoint: US3 complete → MVP DONE

```bash
uv run pytest -v
uv run python manage.py check
uv run ruff check .
uv run ruff format --check .
```

All pass → **MVP IS DONE.** US1 + US2 + US3 deliver a working CRM.

- [ ] S059 MVP checkpoint passed 🎯🎯🎯

---

## Post-MVP (deferred until MVP is validated)

The following user stories are value-adds on top of the MVP.
They are listed here for planning but should NOT be started until
S059 passes.

### US4 — Activities (P2)
- S060: `oportunidades/api/serializers.py` — ActividadSerializer
- S061: `oportunidades/api/filters.py` — ActividadFilter
- S062: `oportunidades/api/views.py` — ActividadViewSet
- S063: Tests — test_api_actividades.py

### US5 — Audit log endpoint (P2)
- S064: `audit/api/serializers.py` — AuditLogSerializer
- S065: `audit/api/filters.py` — AuditLogFilter
- S066: `audit/api/views.py` — AuditLogViewSet (read-only)
- S067: Tests — audit/tests/test_api.py

### US6 — CSV export (P2)
- S068: `clientes/api/renderers.py` — CSVRenderer
- S069: `clientes/api/mixins.py` — CSVExportMixin
- S070: Apply mixin to ClienteViewSet, OportunidadViewSet
- S071: Tests — test_api_export.py

### US7 — Saved searches (P3)
- S072: `core/api/serializers.py` — BusquedaGuardadaSerializer
- S073: `core/api/views.py` — BusquedaGuardadaViewSet
- S074: Tests — test_busquedas.py

### US8 — Dashboard refinements (P3)
- S075: Dashboard win_rate calculation
- S076: Dashboard excludes archived
- S077: Tests — test_dashboard refinements

---

## Execution order summary

```
Phase 0 (core abstracts)     S001 → S005     [5 steps]
Phase 1 (business models)    S010 → S019     [10 steps]
Phase 2 (services+signals)   S020 → S030     [11 steps]
Phase 3 (US1 Auth)           S031 → S034     [4 steps]
Phase 4 (US2 Clientes)       S035 → S044     [10 steps]
Phase 5 (US3 Pipeline+Dash)  S045 → S059     [15 steps]
                                              ─────────
                                              55 steps to MVP
```

Each step is one file or one model. Each step has a verification
command. Stop at any checkpoint to validate independently.

**MVP = S001 through S059.** Everything after S059 is post-MVP.
