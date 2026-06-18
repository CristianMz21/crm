---

description: "Task list for CRM MVP implementation"
---

# Tasks: CRM MVP

**Input**: Spec from `specs/001-crm-mvp/spec.md`, plan from
`specs/001-crm-mvp/plan.md`, data model from `data-model.md`,
research from `research.md`.

**Prerequisites**: All four documents are in place. Tasks below
assume the current repo state: `Cliente` and `Contacto` models
exist; the rest of the schema and the entire API need to be built.

**Organization**: Tasks are grouped by user story, then by phase.
Each user story can be implemented and tested independently. The
MVP is user story 1 + 2 + 3 (P1).

**Format**: `[ID] [P?] [Story] Description`
- `[P]` = can run in parallel (different files, no dependencies)
- `[Story]` = which user story the task belongs to (US1..US8)
- File paths are exact and from the repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, configuration.

- [ ] T001 Pin runtime deps in `pyproject.toml` [project.dependencies] (Django, DRF, django-filter, Faker) and dev deps in [dependency-groups] (pytest, pytest-django, django-debug-toolbar, ruff). Spec originally said requirements.txt; amended to pyproject.toml because the project uses uv (uv.lock, .venv present).
- [ ] T002 Add dev tooling in `pyproject.toml` (ruff config, pytest config with `DJANGO_SETTINGS_MODULE = "config.settings"`)
- [ ] T003 [P] Create the `pipeline/` Django app skeleton: `apps.py`, `models.py` (empty), `migrations/`, `tests/`
- [ ] T004 [P] Create the `audit/` Django app skeleton: `apps.py`, `models.py` (empty), `migrations/`, `tests/`
- [ ] T005 [P] Create the `dashboard/` Django app skeleton: `apps.py`, `views.py` (empty), `urls.py`, `tests/`
- [ ] T006 Register new apps in `INSTALLED_APPS` in `config/settings.py`
- [ ] T007 Configure `REST_FRAMEWORK` in `config/settings.py` (default auth, permission, pagination page size 25)
- [ ] T008 [P] Wire `django-debug-toolbar` in `config/settings.py` and `config/urls.py` (dev only)
- [ ] T009 Add `pytest.ini` (or pyproject) with `DJANGO_SETTINGS_MODULE`, `python_files = ["test_*.py"]`, `testpaths = ["<app>/tests"]`

**Checkpoint**: `python manage.py check` is clean. `pytest --collect-only` runs.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that blocks all user story work.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [ ] T010 Create `pipeline/models.py`: `Pipeline` and `Etapa` with unique_together on `(pipeline, orden)`
- [ ] T011 Create `audit/models.py`: `AuditLog` with `actor`, `action`, `model`, `object_id`, `object_repr`, `changes` (JSONField), `timestamp`, plus the two indexes
- [ ] T012 Add `clientes/models.py:Oportunidad` and `clientes/models.py:Actividad` and `clientes/models.py:Etiqueta` per `data-model.md`
- [ ] T013 Update `clientes/models.py:Cliente` to add `pais`, `sitio_web`, `notas`, `fecha_modificacion`, `creado_por` per `data-model.md`
- [ ] T014 Create `clientes/managers.py` with `ClienteManager` and `objects_all` (and equivalents for Contacto, Oportunidad, Actividad, Etiqueta)
- [ ] T015 Create `clientes/services/pipeline.py` with `ensure_default_pipeline()` and `mover_etapa(oportunidad, etapa_id, *, actor)`
- [ ] T016 Create `clientes/services/audit.py` with `compute_diff(instance, old_dict)` and the audit-emit helper
- [ ] T017 Create `clientes/signals.py` with the `post_save` and `post_delete` handlers for Cliente, Contacto, Oportunidad, Actividad, Etiqueta
- [ ] T018 Register signals in `clientes/apps.py:ready()` and `pipeline/apps.py:ready()`
- [ ] T019 Create data migration `clientes/migrations/0002_seed_default_pipeline.py` that calls `ensure_default_pipeline`
- [ ] T020 Add a `clientes/tests/conftest.py` with fixtures: `owner`, `cliente`, `cliente_con_contactos`, `oportunidad_ganada`, `etapa_ganado`, `api_client`
- [ ] T021 Create `clientes/api/serializers.py` skeletons (empty for now)
- [ ] T022 Create `clientes/api/views.py` skeletons (empty for now)
- [ ] T023 Create `clientes/api/filters.py` skeletons (empty for now)
- [ ] T024 Create `clientes/api/urls.py` with the `DefaultRouter` (empty registrations for now)
- [ ] T025 Wire `path("api/", include("clientes.api.urls"))` in `config/urls.py`
- [ ] T026 Configure `SessionAuthentication` and login redirect URL in `config/settings.py` and a `LOGIN_URL = "/api/auth/login/"`
- [ ] T027 Add a minimal `templates/base.html`, `templates/registration/login.html`, `templates/registration/logged_out.html`
- [ ] T028 Update `clientes/admin.py` to register all 5 business models + Pipeline + Etapa + AuditLog
- [ ] T029 Make `python manage.py migrate` succeed and `python manage.py createsuperuser` work
- [ ] T030 Make `pytest --collect-only` succeed (no test files required yet, but discovery works)

**Checkpoint**: `python manage.py migrate` works. `pytest --collect-only` works. Schema matches `data-model.md`. Default pipeline is seeded.

---

## Phase 3: User Story 1 - Authenticate and reach my dashboard (Priority: P1) 🎯 MVP

**Goal**: Owner can log in and reach the API; unauthenticated API calls return 403.

**Independent Test**: `pytest clientes/tests/test_api_auth.py` passes; an unauthenticated `APIClient` to `/api/clientes/` returns 403; a logged-in client returns 200.

### Tests for User Story 1 (REQUIRED per constitution principle VIII)

- [ ] T031 [P] [US1] `clientes/tests/test_api_auth.py::test_unauthenticated_request_returns_403`
- [ ] T032 [P] [US1] `clientes/tests/test_api_auth.py::test_authenticated_request_returns_200`
- [ ] T033 [P] [US1] `clientes/tests/test_api_auth.py::test_login_with_bad_credentials_returns_400`
- [ ] T034 [P] [US1] `clientes/tests/test_api_auth.py::test_logout_clears_session`

### Implementation for User Story 1

- [ ] T035 [US1] Add `clientes/api/views.py:AuthViewSet` with `me`, `login`, `logout` actions (depends on T022)
- [ ] T036 [US1] Register `AuthViewSet` in `clientes/api/urls.py` (depends on T035)
- [ ] T037 [US1] Verify `pytest clientes/tests/test_api_auth.py` is green

**Checkpoint**: US1 is complete. Owner can log in via the browser and via curl.

---

## Phase 4: User Story 2 - Manage clients and contacts (Priority: P1) 🎯 MVP

**Goal**: Owner can CRUD clients, search, filter, soft-delete, and manage nested contacts.

**Independent Test**: All `test_api_clientes.py` tests pass; `assertNumQueries` for the list is bounded; soft-deleted clients are absent from default listings.

### Tests for User Story 2 (REQUIRED)

- [ ] T038 [P] [US2] `clientes/tests/test_api_clientes.py::test_crear_cliente_exitoso_devuelve_201`
- [ ] T039 [P] [US2] `clientes/tests/test_api_clientes.py::test_crear_cliente_con_email_invalido_devuelve_400`
- [ ] T040 [P] [US2] `clientes/tests/test_api_clientes.py::test_crear_cliente_con_email_duplicado_devuelve_400`
- [ ] T041 [P] [US2] `clientes/tests/test_api_clientes.py::test_listar_clientes_paginado`
- [ ] T042 [P] [US2] `clientes/tests/test_api_clientes.py::test_filtrar_por_ciudad`
- [ ] T043 [P] [US2] `clientes/tests/test_api_clientes.py::test_filtrar_por_activo`
- [ ] T044 [P] [US2] `clientes/tests/test_api_clientes.py::test_search_case_insensitive`
- [ ] T045 [P] [US2] `clientes/tests/test_api_clientes.py::test_detalle_cliente_incluye_contactos`
- [ ] T046 [P] [US2] `clientes/tests/test_api_clientes.py::test_actualizar_cliente`
- [ ] T047 [P] [US2] `clientes/tests/test_api_clientes.py::test_borrar_cliente_es_soft_delete`
- [ ] T048 [P] [US2] `clientes/tests/test_api_clientes.py::test_borrar_cliente_no_aparece_en_listado`
- [ ] T049 [P] [US2] `clientes/tests/test_api_clientes.py::test_crear_contacto_anidado`
- [ ] T050 [P] [US2] `clientes/tests/test_api_clientes.py::test_borrar_cliente_cascada_contactos`

### ORM tests (N+1 regression per constitution principle V)

- [ ] T051 [US2] `clientes/tests/test_orm.py::test_listar_clientes_no_hace_n_plus_1` using `assertNumQueries`
- [ ] T052 [US2] `clientes/tests/test_orm.py::test_detalle_cliente_constante_queries` using `assertNumQueries`

### Implementation for User Story 2

- [ ] T053 [P] [US2] `clientes/api/serializers.py:ContactoSerializer`
- [ ] T054 [P] [US2] `clientes/api/serializers.py:ClienteSerializer` (with nested `contactos` and `actividades`)
- [ ] T055 [P] [US2] `clientes/api/serializers.py:ClienteDetailSerializer` (extends ClienteSerializer with nested relations)
- [ ] T056 [US2] `clientes/api/filters.py:ClienteFilter` with `ciudad`, `activo`, `search` (django-filter)
- [ ] T057 [US2] `clientes/api/views.py:ClienteViewSet` with `get_serializer_class` (depends on T053..T056)
- [ ] T058 [US2] `clientes/api/views.py:ContactoViewSet` for nested routes (depends on T053)
- [ ] T059 [US2] Register `ClienteViewSet` and `ContactoViewSet` in `clientes/api/urls.py`
- [ ] T060 [US2] Verify `pytest clientes/tests/test_api_clientes.py clientes/tests/test_orm.py` is green
- [ ] T061 [US2] `clientes/tests/test_audit.py::test_create_cliente_escribe_audit_log` (audit log covers Cliente)
- [ ] T062 [US2] `clientes/tests/test_audit.py::test_update_cliente_escribe_audit_log_con_diff`
- [ ] T063 [US2] `clientes/tests/test_audit.py::test_delete_cliente_escribe_audit_log`

**Checkpoint**: US2 is complete. The owner can manage clients and contacts from the API, with bounded query counts and audit log entries.

---

## Phase 5: User Story 3 - Move opportunities through a pipeline (Priority: P1) 🎯 MVP

**Goal**: Owner can create opportunities, move them between stages, see dashboard metrics.

**Independent Test**: `test_api_oportunidades.py` and `test_dashboard.py` pass; `mover_etapa` sets `fecha_cierre` on Ganado and clears it on stage-out.

### Tests for User Story 3 (REQUIRED)

- [ ] T064 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_crear_oportunidad_exitosa`
- [ ] T065 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_crear_oportunidad_sin_monto_devuelve_400`
- [ ] T066 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_mover_a_etapa_ganado_setea_fecha_cierre`
- [ ] T067 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_mover_a_etapa_perdido_setea_fecha_cierre`
- [ ] T068 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_mover_desde_cerrado_a_abierta_limpia_fecha_cierre`
- [ ] T069 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_filtrar_oportunidades_por_etapa`
- [ ] T070 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_filtrar_oportunidades_por_monto_range`
- [ ] T071 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_filtrar_oportunidades_por_asignado_a`
- [ ] T072 [P] [US3] `clientes/tests/test_api_oportunidades.py::test_listar_oportunidades_paginado`

### ORM tests

- [ ] T073 [US3] `clientes/tests/test_orm.py::test_listar_oportunidades_no_hace_n_plus_1`
- [ ] T074 [US3] `clientes/tests/test_orm.py::test_detalle_oportunidad_constante_queries`

### Implementation for User Story 3

- [ ] T075 [P] [US3] `clientes/api/serializers.py:OportunidadSerializer` with Decimal as string output
- [ ] T076 [P] [US3] `clientes/api/filters.py:OportunidadFilter` with `etapa`, `cliente`, `monto__gte`, `monto__lte`, `asignado_a`, `search`
- [ ] T077 [US3] `clientes/api/views.py:OportunidadViewSet` with a `mover_etapa` custom action (depends on T075, T076, and T015)
- [ ] T078 [US3] Register `OportunidadViewSet` in `clientes/api/urls.py`
- [ ] T079 [US3] Verify `pytest clientes/tests/test_api_oportunidades.py clientes/tests/test_orm.py` is green
- [ ] T080 [US3] `clientes/tests/test_pipeline.py::test_ensure_default_pipeline_crea_4_etapas`
- [ ] T081 [US3] `clientes/tests/test_pipeline.py::test_no_se_puede_tener_mas_de_un_pipeline_default`
- [ ] T082 [US3] `clientes/tests/test_audit.py::test_create_oportunidad_escribe_audit_log`
- [ ] T083 [US3] `clientes/tests/test_audit.py::test_mover_etapa_escribe_audit_log`

### Dashboard endpoint

- [ ] T084 [US3] `dashboard/services.py:compute_dashboard_metrics()` returning the dict per `api.yaml`
- [ ] T085 [US3] `dashboard/views.py:DashboardView` (GET only, no auth beyond session)
- [ ] T086 [US3] `dashboard/urls.py` with one route
- [ ] T087 [P] [US3] `dashboard/tests/test_dashboard.py::test_dashboard_devuelve_pipeline_por_etapa`
- [ ] T088 [P] [US3] `dashboard/tests/test_dashboard.py::test_dashboard_devuelve_ganado_y_perdido_del_mes`
- [ ] T089 [P] [US3] `dashboard/tests/test_dashboard.py::test_dashboard_sin_datos_devuelve_zero_no_500`
- [ ] T090 [P] [US3] `dashboard/tests/test_dashboard.py::test_dashboard_devuelve_top_5_abiertos`
- [ ] T091 [US3] `dashboard/tests/test_dashboard.py::test_dashboard_un_query_por_metrica` (assertNumQueries)

**Checkpoint**: US3 is complete. The owner can create opportunities, move them, and see the dashboard.

**🎯 MVP at this point**: US1 + US2 + US3 deliver a working CRM. Stop, validate, demo, ship.

---

## Phase 6: User Story 4 - Log activities against clients and opportunities (Priority: P2)

**Goal**: Owner can record activities linked to clients and optionally opportunities.

**Independent Test**: `test_api_actividades.py` passes; activities appear in client detail.

### Tests for User Story 4 (REQUIRED)

- [ ] T092 [P] [US4] `clientes/tests/test_api_actividades.py::test_crear_actividad_contra_cliente`
- [ ] T093 [P] [US4] `clientes/tests/test_api_actividades.py::test_crear_actividad_contra_oportunidad`
- [ ] T094 [P] [US4] `clientes/tests/test_api_actividades.py::test_tipo_invalido_devuelve_400`
- [ ] T095 [P] [US4] `clientes/tests/test_api_actividades.py::test_actividades_aparecen_en_detalle_cliente_ordenadas_desc`
- [ ] T096 [P] [US4] `clientes/tests/test_api_actividades.py::test_filtrar_actividades_por_cliente`
- [ ] T097 [P] [US4] `clientes/tests/test_api_actividades.py::test_filtrar_actividades_por_tipo`

### Implementation for User Story 4

- [ ] T098 [P] [US4] `clientes/api/serializers.py:ActividadSerializer`
- [ ] T099 [P] [US4] `clientes/api/filters.py:ActividadFilter`
- [ ] T100 [US4] `clientes/api/views.py:ActividadViewSet`
- [ ] T101 [US4] Register `ActividadViewSet` in `clientes/api/urls.py`
- [ ] T102 [US4] `clientes/api/serializers.py:ClienteDetailSerializer` extended to include `actividades` ordered by `-fecha`
- [ ] T103 [US4] Verify `pytest clientes/tests/test_api_actividades.py` is green
- [ ] T104 [US4] `clientes/tests/test_audit.py::test_create_actividad_escribe_audit_log`

---

## Phase 7: User Story 5 - Audit log on every change (Priority: P2)

**Goal**: Audit log list endpoint; per-object history filter.

### Tests for User Story 5 (REQUIRED)

- [ ] T105 [P] [US5] `audit/tests/test_api.py::test_listar_audit_log_paginado`
- [ ] T106 [P] [US5] `audit/tests/test_api.py::test_filtrar_audit_por_modelo`
- [ ] T107 [P] [US5] `audit/tests/test_api.py::test_filtrar_audit_por_object_id`
- [ ] T108 [P] [US5] `audit/tests/test_api.py::test_filtrar_audit_por_action`
- [ ] T109 [P] [US5] `audit/tests/test_api.py::test_audit_log_de_una_accion_es_inmutable` (no UPDATE on audit)

### Implementation for User Story 5

- [ ] T110 [P] [US5] `audit/api/serializers.py:AuditLogSerializer` (read-only)
- [ ] T111 [P] [US5] `audit/api/filters.py:AuditLogFilter`
- [ ] T112 [US5] `audit/api/views.py:AuditLogViewSet` (read-only `ReadOnlyModelViewSet`)
- [ ] T113 [US5] `audit/api/urls.py` with the router
- [ ] T114 [US5] Wire `path("api/", include("audit.api.urls"))` in `config/urls.py` (alongside `clientes.api.urls`)
- [ ] T115 [US5] Verify `pytest audit/tests/` is green

---

## Phase 8: User Story 6 - Export any list to CSV (Priority: P2)

**Goal**: `?format=csv` on every list endpoint returns a streaming CSV.

### Tests for User Story 6 (REQUIRED)

- [ ] T116 [P] [US6] `clientes/tests/test_api_export.py::test_listar_clientes_csv`
- [ ] T117 [P] [US6] `clientes/tests/test_api_export.py::test_listar_clientes_csv_respeta_filtros`
- [ ] T118 [P] [US6] `clientes/tests/test_api_export.py::test_listar_oportunidades_csv`
- [ ] T119 [P] [US6] `clientes/tests/test_api_export.py::test_listar_actividades_csv`
- [ ] T120 [US6] `clientes/tests/test_api_export.py::test_csv_usa_streaming_para_muchos_registros` (assertNumQueries bounded)

### Implementation for User Story 6

- [ ] T121 [P] [US6] `clientes/api/renderers.py:CSVRenderer` (DRF renderer) and a `csv_export` helper
- [ ] T122 [P] [US6] `clientes/api/mixins.py:CSVExportMixin` (overrides `list` to switch to the CSV renderer when `?format=csv`)
- [ ] T123 [US6] Apply `CSVExportMixin` to `ClienteViewSet`, `OportunidadViewSet`, `ActividadViewSet` (depends on T121, T122)
- [ ] T124 [US6] Verify `pytest clientes/tests/test_api_export.py` is green

---

## Phase 9: User Story 7 - Advanced filtering and saved searches (Priority: P3)

**Goal**: Compound filters; save and execute saved searches.

### Tests for User Story 7

- [ ] T125 [P] [US7] `clientes/tests/test_api_oportunidades.py::test_combinar_filtros_monto_y_etapa`
- [ ] T126 [P] [US7] `clientes/tests/test_api_oportunidades.py::test_filtrar_por_search_en_titulo`
- [ ] T127 [P] [US7] `clientes/tests/test_busquedas.py::test_guardar_busqueda_devuelve_201`
- [ ] T128 [P] [US7] `clientes/tests/test_busquedas.py::test_listar_busquedas_guardadas_del_usuario`
- [ ] T129 [P] [US7] `clientes/tests/test_busquedas.py::test_ejecutar_busqueda_guardada_devuelve_resultados`
- [ ] T130 [P] [US7] `clientes/tests/test_busquedas.py::test_borrar_busqueda_devuelve_204`

### Implementation for User Story 7

- [ ] T131 [P] [US7] `clientes/models.py:BusquedaGuardada` (added to the clientes app, not a new app)
- [ ] T132 [P] [US7] `clientes/api/serializers.py:BusquedaGuardadaSerializer`
- [ ] T133 [P] [US7] `clientes/api/views.py:BusquedaGuardadaViewSet` with `ejecutar` action
- [ ] T134 [US7] Register `BusquedaGuardadaViewSet` in `clientes/api/urls.py`
- [ ] T135 [US7] Verify `pytest clientes/tests/test_busquedas.py` is green

---

## Phase 10: User Story 8 - Dashboard with basic metrics (Priority: P3)

**Goal**: The dashboard endpoint covers all 5 metrics with one query each.

### Tests for User Story 8 (mostly covered in US3)

- [ ] T136 [P] [US8] `dashboard/tests/test_dashboard.py::test_dashboard_calcula_win_rate`
- [ ] T137 [P] [US8] `dashboard/tests/test_dashboard.py::test_dashboard_ignora_oportunidades_archivadas`
- [ ] T138 [P] [US8] `dashboard/tests/test_dashboard.py::test_dashboard_devuelve_oportunidades_del_owner`

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories.

- [ ] T139 [P] Wire `seed.py` to use the new schema (Cliente, Contacto, Oportunidad, Actividad, Etiqueta with the real fields)
- [ ] T140 [P] Add minimal HTML templates: `templates/clientes/cliente_list.html`, `cliente_detail.html`, `cliente_form.html`
- [ ] T141 [P] Add `clientes/views.py` for the HTML routes (login_required decorators)
- [ ] T142 [P] Wire `clientes/urls.py` for the HTML routes (`/clientes/`, `/clientes/<id>/`, `/clientes/nuevo/`)
- [ ] T143 [P] Update `README.md` to point to `specs/001-crm-mvp/` and the spec-kit workflow
- [ ] T144 [P] Update `CHANGELOG.md` with the v0.2.0 entry
- [ ] T145 [P] Update `CONTRIBUTING.md` to reference `.specify/memory/constitution.md` and the spec-kit flow
- [ ] T146 Run `ruff format .` and `ruff check .` on the codebase
- [ ] T147 Run `python manage.py check --deploy` and address any issues that apply to v1
- [ ] T148 Run `pytest` and verify the full suite is green, with timing under 60s
- [ ] T149 Run the full `quickstart.md` end-to-end on a clean checkout
- [ ] T150 Tag `v0.2.0` on `main` and push

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Starts immediately.
- **Foundational (Phase 2)**: Depends on Setup. BLOCKS all user stories.
- **US1 (Phase 3)**: Depends on Foundational.
- **US2 (Phase 4)**: Depends on Foundational. Independent of US1.
- **US3 (Phase 5)**: Depends on Foundational. Independent of US1/US2.
- **US4..US8**: Depend on Foundational. Independent of each other
  (in implementation terms) but US4 needs the data model from
  Foundational, US6 needs the API from US2/US3, US7 needs the
  filtering from US2/US3, US8 is a refinement of US3.

### Recommended Execution Order

1. Phase 1 (Setup)
2. Phase 2 (Foundational)
3. US1 + US2 + US3 in parallel (or sequentially if one person)
4. **STOP and validate MVP** (this is the "ship it" point)
5. US4 + US5 + US6 + US7 + US8 (incremental)
6. Phase 11 (Polish)

### Parallel Opportunities Within Each Phase

- Within a phase, all `[P]`-marked tasks can run in parallel.
- Across phases, once a user story's implementation is done, the
  tests for the NEXT user story can be written in parallel with
  refactor of the previous one.

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete US1, US2, US3 in any order
4. **STOP and VALIDATE**: Run `pytest`, click through the Browsable
   API, demo the pipeline drag, check the audit log
5. Tag v0.2.0 and ship

### Incremental Delivery (P2 + P3)

1. After MVP: ship US4 (activities)
2. Ship US5 (audit log endpoint)
3. Ship US6 (CSV export)
4. Ship US7 (saved searches)
5. Ship US8 (dashboard refinements)
6. Polish

### Solo Strategy

This project is a single-owner build. The phases are designed so a
single developer can move through them sequentially without
re-work. The MVP (US1+US2+US3) is the highest priority and
delivers a usable CRM. The P2 and P3 stories are value-adds.

---

## Notes

- Tasks marked `[P]` run in parallel.
- The `[Story]` label is for traceability. When a task doesn't fit
  one story (e.g. a shared fixture), the label is `[Setup]` or
  `[Foundation]`.
- After each user story, commit with a Conventional Commits message:
  `feat(api): add ClienteViewSet with nested contacts (US2)`.
- Stop at any checkpoint. A working US1+US2+US3 is the MVP. The
  P2 and P3 stories are optional enhancements.
- Verify tests fail BEFORE implementation. The constitution requires
  test-first.
