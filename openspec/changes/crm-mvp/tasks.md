# Tasks — CRM MVP

One section per day. Tasks are checkable. Each task names the file(s) it
touches and the spec requirement(s) it satisfies. Mark with `[x]` only
when the test (or the equivalent manual check) passes.

Day 1 is partially in progress: `Cliente` and `Contacto` models exist
with migrations applied. Tasks that are already done are marked with
`[x]`.

---

## Day 1 — Fundamentals

Goal: recover the model → migration → admin → run server cycle.

Spec coverage: R-MODELS-01, R-MODELS-02.

- [x] 1.1 Create `venv`, activate, install Django + DRF + Faker. Pin in `requirements.txt`.
- [x] 1.2 `django-admin startproject config .`
- [x] 1.3 `python manage.py startapp clientes`
- [x] 1.4 Write `Cliente` model in `clientes/models.py` (all fields per R-MODELS-01).
- [x] 1.5 Write `Contacto` model in `clientes/models.py` (all fields per R-MODELS-02).
- [x] 1.6 `python manage.py makemigrations clientes`
- [x] 1.7 `python manage.py migrate`
- [x] 1.8 Register `Cliente` and `Contacto` in `clientes/admin.py`.
- [x] 1.9 `python manage.py createsuperuser`
- [x] 1.10 Run server, log in to `/admin/`, create 2-3 Clientes by hand.

**Day 1 done when:** Clientes appear in the admin and can be created/edited/deleted from there.

---

## Day 2 — Vanilla views

Goal: views, URLs, templates, basic querysets.

Spec coverage: R-VIEWS-01, R-VIEWS-02, R-VIEWS-03.

- [ ] 2.1 Create view `cliente_list` in `clientes/views.py` (FBV or CBV, your call).
- [ ] 2.2 Create template `templates/clientes/cliente_list.html` with an HTML table.
- [ ] 2.3 Wire URL in `clientes/urls.py` and include in `config/urls.py`.
- [ ] 2.4 Create view `cliente_detail` that shows Cliente + Contactos.
- [ ] 2.5 Create template `templates/clientes/cliente_detail.html`.
- [ ] 2.6 Wire URL `clientes/<int:pk>/`.
- [ ] 2.7 Create `ClienteForm` (ModelForm) for the create view.
- [ ] 2.8 Create view `cliente_create` with GET (show form) and POST (save).
- [ ] 2.9 Create template `templates/clientes/cliente_form.html`.
- [ ] 2.10 Wire URL `clientes/nuevo/`.

**Day 2 done when:** navigating to `/clientes/` shows the list, clicking a row goes to detail showing Contactos, `/clientes/nuevo/` creates a Cliente.

---

## Day 3 — Remaining models + seed

Goal: more complex relations and a real seed.

Spec coverage: R-MODELS-03, R-MODELS-04, R-MODELS-05, R-SEED-01.

- [ ] 3.1 Add `Oportunidad` model in `clientes/models.py` (per R-MODELS-03).
- [ ] 3.2 Add `Actividad` model (per R-MODELS-04).
- [ ] 3.3 Add `Etiqueta` model and M2M (per R-MODELS-05).
- [ ] 3.4 `python manage.py makemigrations clientes` and `migrate`.
- [ ] 3.5 Register the three new models in `clientes/admin.py`.
- [ ] 3.6 Write `seed.py` that creates 50 Clientes with 1-4 Contactos each.
- [ ] 3.7 Seed adds 0-3 Oportunidades per Cliente with mixed `estado`.
- [ ] 3.8 Seed adds 0-5 Actividades per Cliente.
- [ ] 3.9 Seed creates 8 Etiquetas and assigns 1-3 random ones to each Cliente.
- [ ] 3.10 Use `bulk_create` for the bulk inserts.
- [ ] 3.11 Run `python seed.py`; verify in admin.

**Day 3 done when:** running the seed populates 50 Clientes with the expected counts (verifiable via `manage.py shell`).

---

## Day 4 — DRF API

Goal: turn the CRM into a REST API. This is the closest day to the interview format.

Spec coverage: R-API-01, R-API-02, R-API-03, R-API-04.

- [ ] 4.1 Add `clientes/api/` package with `__init__.py`, `serializers.py`, `views.py`, `urls.py`, `filters.py`.
- [ ] 4.2 Add `rest_framework` to `INSTALLED_APPS`.
- [ ] 4.3 Add `REST_FRAMEWORK` config to `config/settings.py` with pagination (PAGE_SIZE=10).
- [ ] 4.4 Add `path("api/", include("clientes.api.urls"))` to `config/urls.py`.
- [ ] 4.5 Implement `ContactoSerializer` (ModelSerializer) in `serializers.py`.
- [ ] 4.6 Implement `ClienteSerializer` with `contactos = ContactoSerializer(many=True, read_only=True)`.
- [ ] 4.7 Add `validate_email` to `ClienteSerializer` rejecting `*@test.com`.
- [ ] 4.8 Implement `OportunidadSerializer` with `validate(self, attrs)` enforcing `ganado` requires `fecha_cierre`.
- [ ] 4.9 Implement `ClienteViewSet(viewsets.ModelViewSet)` with `queryset` and `serializer_class`.
- [ ] 4.10 Implement `ContactoViewSet` and `OportunidadViewSet`.
- [ ] 4.11 Override `get_queryset` in `ClienteViewSet` to filter by `?ciudad=...` and `?activo=...`.
- [ ] 4.12 Register all three viewsets in `clientes/api/urls.py` via `DefaultRouter`.

**Day 4 done when:** the Browsable API at `/api/clientes/` lists, filters, and paginates; POST with forbidden email returns 400; POST with `estado=ganado` and no `fecha_cierre` returns 400.

---

## Day 5 — ORM intensive

Goal: master queries, fix N+1.

Spec coverage: R-ORM-01, R-ORM-02, R-ORM-03.

- [ ] 5.1 Install and wire `django-debug-toolbar` (INSTALLED_APPS, middleware, urls).
- [ ] 5.2 Verify the toolbar appears in any `/clientes/<pk>/` request.
- [ ] 5.3 Write the OR-with-Q query (R-ORM-01) in `clientes/views.py` or `manage.py shell`.
- [ ] 5.4 Write the total-ganado aggregation (R-ORM-02).
- [ ] 5.5 Write the avg-by-estado aggregation.
- [ ] 5.6 Write the annotate-with-sum-by-cliente query.
- [ ] 5.7 Implement `cliente_detail_optimized` view in `clientes/views.py` (or improve existing) using `select_related` + `prefetch_related`.
- [ ] 5.8 Note query count BEFORE optimization in `openspec/changes/crm-mvp/verify-report.md` (or the design).
- [ ] 5.9 Note query count AFTER optimization.
- [ ] 5.10 Write `test_orm.py::test_detalle_cliente_no_hace_n_mas_1` using `CaptureQueriesContext` + `assertNumQueries` (R-ORM-03).

**Day 5 done when:** you can explain in plain Spanish why `select_related` is for FK and `prefetch_related` for M2M/reverse, and you can SHOW the query count going down with the toolbar.

---

## Day 6 — Testing, manager, signal

Goal: tests that lock in the contracts, plus the two cross-cutting layers.

Spec coverage: R-TEST-01..04, R-MGR-01, R-MGR-02, R-SIG-01.

- [ ] 6.1 Add `pytest` and `pytest-django` to `requirements.txt` (or `requirements-dev.txt`).
- [ ] 6.2 Configure `DJANGO_SETTINGS_MODULE` in `pyproject.toml` under `[tool.pytest.ini_options]`.
- [ ] 6.3 Create `clientes/tests/conftest.py` with fixtures: `cliente`, `cliente_con_contactos`, `oportunidad_ganada`, `api_client`.
- [ ] 6.4 Write `test_models.py::test_str_cliente_devuelve_nombre` (R-TEST-01).
- [ ] 6.5 Write `test_models.py::test_email_unico_rechaza_duplicado` (R-TEST-02).
- [ ] 6.6 Write `test_api.py::test_crear_cliente_con_email_prohibido_devuelve_400` (R-TEST-03).
- [ ] 6.7 Write `test_api.py::test_oportunidad_ganada_sin_fecha_cierre_falla` (R-TEST-04).
- [ ] 6.8 Create `clientes/managers.py` with `ClienteQuerySet.activos()` and `con_oportunidades_ganadas()`.
- [ ] 6.9 Wire the manager in `Cliente` as `objects = ClienteManager.from_queryset(ClienteQuerySet)()`.
- [ ] 6.10 Use `Cliente.activos.all()` in at least one view (R-MGR-01).
- [ ] 6.11 Create `clientes/signals.py` with `post_save` handler for `Oportunidad` (R-SIG-01).
- [ ] 6.12 Make the signal idempotent: do not create a duplicate Actividad on repeat saves.
- [ ] 6.13 Register the signal in `clientes/apps.py:ready()`.
- [ ] 6.14 Write `test_signals.py::test_oportunidad_ganada_crea_actividad`.
- [ ] 6.15 Run `pytest`; all green.

**Day 6 done when:** `pytest` reports all tests passing, including the `assertNumQueries` test from day 5.

---

## Day 7 — Timed rebuild

Goal: measure fluency recovery. NO AI. NO looking at prior code.

- [ ] 7.1 Copy the project to a fresh location; strip the `clientes` app.
- [ ] 7.2 Start a 90-minute timer.
- [ ] 7.3 Rebuild: `Cliente` + `Oportunidad` models, migrations, one serializer with validation, one ViewSet, one optimized query.
- [ ] 7.4 Stop the timer; record the actual time.
- [ ] 7.5 Compare against day 4-6 times.
- [ ] 7.6 Decide if ready for the interview (target: < 90 min).

**Day 7 done when:** you have a measurement, and you know whether the practice was enough.

---

## Cross-day housekeeping

- [ ] Add `pytest`, `pytest-django`, `django-debug-toolbar`, `Faker` to `requirements.txt` before day 5.
- [ ] Add `db.sqlite3` to `.gitignore`.
- [ ] Add `.venv/` to `.gitignore`.
- [ ] Once `pytest` is green, run `python manage.py check` and capture the output in `verify-report.md`.

---

## Definition of done for the whole change

The change is ready to archive when:

- Every day 1-6 task is checked.
- `pytest` passes.
- `python manage.py check` is clean.
- `verify-report.md` lists every spec scenario with verdict COMPLIANT or
  EXPLICITLY UNTESTED (with reason).
