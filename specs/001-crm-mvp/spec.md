# Feature Specification: CRM MVP

**Feature Branch**: `001-crm-mvp`

**Created**: 2026-06-18

**Status**: Draft

**Input**: A real, productive CRM for solo salespeople and small teams.
Built by hand on Django 6 + DRF. Single-user auth, pipeline with
stages, opportunities with assignment, activities log, audit log,
advanced filtering, CSV export, and a test suite that locks the
contracts.

## User Scenarios & Testing

### User Story 1 - Authenticate and reach my dashboard (Priority: P1)

As the owner of this CRM, I want to log in with a username and
password so that no one else can see my client and opportunity data.

**Why this priority**: Without auth, the CRM is not safe to deploy
anywhere reachable. This is the gate to every other story.

**Independent Test**: A user can visit `/admin/login/` and the
`/api/`, get redirected to a login form, submit valid credentials,
and be redirected to a working landing page. Unauthenticated requests
to `/api/clientes/` get a 401 or 403.

**Acceptance Scenarios**:

1. **Given** an unauthenticated visitor, **When** they GET
   `/api/clientes/`, **Then** the response is 401 (or 403 with a
   `WWW-Authenticate: Basic` / redirect to login).
2. **Given** an authenticated owner, **When** they GET
   `/api/clientes/`, **Then** the response is 200 with a paginated
   list of clients.
3. **Given** the owner with valid credentials, **When** they POST
   to `/api/auth/login/`, **Then** a session cookie is set and they
   are authenticated.
4. **Given** the owner, **When** they POST to `/api/auth/logout/`,
   **Then** the session is destroyed and subsequent API calls
   require re-authentication.

---

### User Story 2 - Manage clients and contacts (Priority: P1)

As the owner, I want to create, list, view, edit, and archive clients
and their contacts so that I can keep my book of business in one
place.

**Why this priority**: Clients are the entity the rest of the CRM
relates to. Without CRUD on clients, opportunities have nothing to
attach to. This is the first business-meaningful story.

**Independent Test**: The owner can POST a client with name and
email, list clients with search and filters, retrieve one client
with its contacts nested, update any field, and archive (soft
delete) a client that no longer shows up in default listings.

**Acceptance Scenarios**:

1. **Given** a valid client payload (name, email), **When** the
   owner POSTs to `/api/clientes/`, **Then** the response is 201
   and the client exists in the database.
2. **Given** 30 clients exist, **When** the owner GETs
   `/api/clientes/`, **Then** the response is paginated (10 per
   page by default) and the page shows up to 10 results.
3. **Given** 30 clients exist with various `ciudad` values,
   **When** the owner GETs `/api/clientes/?ciudad=Cali&search=acme`,
   **Then** only clients matching both `ciudad=Cali` and a
   case-insensitive substring match on name or email are returned.
4. **Given** a client exists, **When** the owner GETs
   `/api/clientes/<id>/`, **Then** the response includes the client
   fields plus a `contactos` array of all non-archived contacts.
5. **Given** a client exists, **When** the owner DELETEs
   `/api/clientes/<id>/`, **Then** the client is archived (not hard
   deleted), it no longer appears in `/api/clientes/`, and a GET on
   its detail URL returns 404.
6. **Given** a client with an invalid email, **When** the owner
   POSTs to `/api/clientes/`, **Then** the response is 400 with
   an `email` field error.

---

### User Story 3 - Move opportunities through a pipeline (Priority: P1)

As the owner, I want to create opportunities attached to a client,
move them between stages, and see the total value of my pipeline so
that I can focus my effort on the deals that matter.

**Why this priority**: Opportunities are the unit of revenue. The
pipeline is the operational backbone. Without this story, the CRM
is just an address book.

**Independent Test**: The owner creates a pipeline with at least 4
stages (Nuevo, En proceso, Ganado, Perdido). They create an
opportunity attached to a client. They can move the opportunity
between stages via a dedicated action and see the deal value in the
current stage. Closing a deal as Ganado or Perdido records
`fecha_cierre` automatically.

**Acceptance Scenarios**:

1. **Given** a client and a pipeline with 4 stages, **When** the
   owner POSTs to `/api/oportunidades/` with `cliente`, `titulo`,
   `monto`, and `etapa=<nuevo>`, **Then** the response is 201 and
   the opportunity is in the first stage.
2. **Given** an opportunity in stage "En proceso", **When** the
   owner POSTs to `/api/oportunidades/<id>/mover_etapa/` with
   `etapa=<ganado>`, **Then** the opportunity is in the Ganado
   stage and `fecha_cierre` is set to today.
3. **Given** an opportunity in stage "Perdido", **When** the
   owner GETs `/api/oportunidades/?estado_cerrado=true`, **Then**
   the opportunity appears in the response.
4. **Given** 3 opportunities in the Ganado stage with totals
   $1000, $2000, $5000, **When** the owner GETs
   `/api/dashboard/pipeline/`, **Then** the response includes a
   per-stage breakdown with sums.

---

### User Story 4 - Log activities against clients and opportunities (Priority: P2)

As the owner, I want to record calls, meetings, and notes against a
client (and optionally an opportunity) so that I have a history of
interactions I can review before reaching out again.

**Why this priority**: Without activities, the owner has no audit
trail of what they did. The system is less useful than a notebook.
Important but not blocking the MVP.

**Independent Test**: The owner can create an activity of any
allowed type (llamada, email, reunion) against a client, optionally
linking it to an opportunity. The client detail view shows
activities in reverse chronological order.

**Acceptance Scenarios**:

1. **Given** a client exists, **When** the owner POSTs to
   `/api/actividades/` with `cliente`, `tipo=llamada`, and `nota`,
   **Then** the response is 201 and the activity is recorded.
2. **Given** an opportunity exists, **When** the owner POSTs to
   `/api/actividades/` with `cliente`, `oportunidad`, `tipo=email`,
   and `nota`, **Then** the activity is linked to both.
3. **Given** 5 activities against a client, **When** the owner
   GETs `/api/clientes/<id>/`, **Then** the response includes an
   `actividades` array sorted by `fecha` descending.

---

### User Story 5 - Audit log on every change (Priority: P2)

As the owner, I want every create, update, and delete on business
data to leave a trail so that I can investigate when something looks
wrong.

**Why this priority**: This is about trust. A CRM that quietly
loses data or that the owner can't audit is a CRM that gets
abandoned.

**Independent Test**: When the owner creates, updates, or archives
a client or opportunity, an `AuditLog` entry is created with the
actor, the action, the model, the object id, the timestamp, and a
JSON diff of the changes.

**Acceptance Scenarios**:

1. **Given** a logged-in owner, **When** they create a client via
   POST `/api/clientes/`, **Then** an `AuditLog` entry exists with
   `action=create`, `model=Cliente`, `object_id=<id>`,
   `actor=<owner>`, and `changes` containing the new field values.
2. **Given** a client, **When** the owner PATCHes
   `/api/clientes/<id>/` with a new `telefono`, **Then** an
   `AuditLog` entry exists with `action=update` and `changes`
   showing only the changed field, with the old and new value.
3. **Given** the owner, **When** they GET `/api/audit/?model=Cliente`,
   **Then** the response is paginated with the most recent entries
   first.

---

### User Story 6 - Export any list to CSV (Priority: P2)

As the owner, I want to export the current filtered list of clients,
opportunities, or activities to CSV so that I can share it with
partners, accountants, or anyone who doesn't use the CRM.

**Independent Test**: The owner can append `?format=csv` to any
list endpoint and receive a CSV download with the visible columns
and the current filter applied.

**Acceptance Scenarios**:

1. **Given** 15 clients, **When** the owner GETs
   `/api/clientes/?format=csv`, **Then** the response is
   `Content-Type: text/csv` with a header row and 15 data rows.
2. **Given** 15 clients, **When** the owner GETs
   `/api/clientes/?ciudad=Cali&format=csv`, **Then** only clients
   in Cali appear in the CSV.
3. **Given** 1 million opportunities (hypothetical), **When** the
   owner GETs `/api/oportunidades/?format=csv`, **Then** the
   response streams the CSV and the server does not load the full
   queryset into memory.

---

### User Story 7 - Advanced filtering and saved searches (Priority: P3)

As the owner, I want to combine multiple filters and save them so
that I can return to my most useful views quickly.

**Independent Test**: The owner can filter opportunities by
`cliente`, `etapa`, `monto__gte`, `monto__lte`, `fecha_cierre__gte`,
and `asignado_a` in any combination. They can save a search with a
name and retrieve it.

**Acceptance Scenarios**:

1. **Given** 20 opportunities, **When** the owner GETs
   `/api/oportunidades/?monto__gte=1000&monto__lte=10000&etapa=2`,
   **Then** only opportunities in the range and stage are
   returned.
2. **Given** a saved search, **When** the owner GETs
   `/api/busquedas_guardadas/`, **Then** the saved search is
   listed.
3. **Given** a saved search id, **When** the owner GETs
   `/api/busquedas_guardadas/<id>/ejecutar/`, **Then** the
   underlying queryset is applied and the results are returned.

---

### User Story 8 - Dashboard with basic metrics (Priority: P3)

As the owner, I want a single screen that shows me my pipeline
value, win rate, and the deals that need attention so that I can
plan my day.

**Independent Test**: The owner visits a dashboard endpoint that
returns aggregated metrics: pipeline value per stage, won total
this month, lost total this month, win rate (ganado / cerrado), and
the top 5 deals by amount that are still open.

**Acceptance Scenarios**:

1. **Given** data exists, **When** the owner GETs
   `/api/dashboard/`, **Then** the response includes `pipeline_por_etapa`,
   `ganado_mes_actual`, `perdido_mes_actual`, `win_rate`, and
   `top_5_abiertos`.
2. **Given** no data, **When** the owner GETs `/api/dashboard/`,
   **Then** the response includes the same keys with zero or empty
   values, never a 500.

---

## Edge Cases

- **Empty state on every list endpoint**: the system returns a 200
  with `{"count": 0, "results": []}`, not a 404.
- **Soft-deleted parent**: a contact whose client is archived no
  longer appears in the client's `contactos` array.
- **Pipeline with no stages**: creating an opportunity is rejected
  with a 400 until the user has set up the pipeline.
- **Decimal arithmetic at the boundary**: amounts submitted as
  strings ("1000.50") are accepted; amounts submitted as floats
  (1000.5) are accepted but converted to Decimal; the API never
  returns a float for a monetary field.
- **Time zone**: all timestamps are stored in UTC and returned in
  ISO 8601 with the user's configured time zone. For this MVP, the
  user has a single configured time zone and the API returns UTC.
- **Search query length**: searches are bounded to 100 characters
  to avoid pathological patterns.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST authenticate the owner via username
  and password (Django built-in auth). No third-party SSO in v1.
- **FR-002**: The system MUST return 401 (or 403 with a redirect
  for HTML clients) for any unauthenticated request to a
  business-data endpoint.
- **FR-003**: The system MUST allow the owner to create, list,
  retrieve, update, and soft-delete clients via the API and the
  admin.
- **FR-004**: The system MUST allow the owner to manage contacts
  nested under a client.
- **FR-005**: The system MUST allow the owner to define a pipeline
  with ordered stages and a default set of stages
  (Nuevo, En proceso, Ganado, Perdido) seeded on first run.
- **FR-006**: The system MUST allow the owner to create, list,
  retrieve, update, and move opportunities between stages.
- **FR-007**: The system MUST auto-set `fecha_cierre` to the current
  date when an opportunity is moved to Ganado or Perdido.
- **FR-008**: The system MUST allow the owner to log activities of
  type `llamada`, `email`, or `reunion` against a client, optionally
  linked to an opportunity.
- **FR-009**: The system MUST write an `AuditLog` entry for every
  create, update, and soft-delete on `Cliente`, `Contacto`,
  `Oportunidad`, `Actividad`, and `Etiqueta`.
- **FR-010**: The system MUST support CSV export of any list
  endpoint via `?format=csv`, streaming the response for lists over
  1000 items.
- **FR-011**: The system MUST support filtering on
  `?ciudad=&activo=&search=` for clients, and on
  `?etapa=&cliente=&monto__gte=&monto__lte=&asignado_a=&search=`
  for opportunities, via `django-filter`.
- **FR-012**: The system MUST provide a dashboard endpoint that
  returns pipeline-by-stage totals, current-month won and lost
  totals, win rate, and top open opportunities.
- **FR-013**: The system MUST persist monetary values as `Decimal`
  with at most 2 decimal places.
- **FR-014**: The system MUST return paginated JSON for every list
  endpoint, default page size 25, configurable per-request.
- **FR-015**: The system MUST return structured error JSON with a
  `code` and `message` for every failure response.

### Key Entities

- **User**: The Django built-in `auth.User`. The system assumes a
  single owner in v1, but the data model supports more.
- **Cliente**: A company or person in the owner's book of business.
  Has name, email, phone, company, city, country, tags, and a soft
  delete flag.
- **Contacto**: A person at a `Cliente`. Has name, role, email,
  phone, and notes.
- **Pipeline**: A named collection of stages. Exactly one pipeline
  is created on first run.
- **Etapa**: A stage in a pipeline, with an integer order, a name,
  and a `cerrada` flag (true for Ganado and Perdido).
- **Oportunidad**: A deal. Has a `cliente`, a `titulo`, a `monto`
  (Decimal), a current `etapa`, an `asignado_a` (User), and a
  `fecha_cierre` set when the stage becomes Ganado or Perdido.
- **Actividad**: An interaction. Has a `cliente`, an optional
  `oportunidad`, a `tipo` (llamada, email, reunion), a `nota`, and
  an auto-set `fecha`.
- **Etiqueta**: A reusable tag. M2M with Cliente.
- **AuditLog**: A row per mutation. Has `actor`, `action`
  (create, update, delete), `model`, `object_id`, `timestamp`, and
  `changes` (JSON).
- **BusquedaGuardada**: A named, saved filter on a list endpoint.
  Has a `nombre`, the `endpoint`, and a JSON `filtros`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The owner can complete a full
  login → create client → create opportunity → move to Ganado →
  see it in the dashboard flow in under 2 minutes.
- **SC-002**: Every list endpoint responds in under 200ms for a
  database with 10,000 clients and 50,000 opportunities.
- **SC-003**: The full `pytest` suite runs in under 60 seconds.
- **SC-004**: `assertNumQueries` tests pass: list view of clients
  uses a constant number of queries (independent of N), detail view
  of a client uses at most 5 queries (1 + 4 prefetches).
- **SC-005**: Zero P0 bugs in the audit log: every create, update,
  and soft-delete on the five business models produces an entry.
- **SC-006**: CSV export of 50,000 opportunities completes in under
  5 seconds and uses less than 100MB of memory.
- **SC-007**: 100% of API endpoints have at least one happy-path
  test and one failure-mode test.

## Assumptions

- The owner has stable internet access and runs the CRM on a single
  host. Multi-tenant deployment is out of scope for v1.
- The owner uses a modern browser (latest Chrome, Firefox, or
  Safari). Internet Explorer is not supported.
- The owner is comfortable with the Django admin for occasional
  one-off data fixes. The custom web UI is minimal.
- Email sending is out of scope. Activities of type `email` are
  notes about emails already sent from elsewhere.
- The system is single-currency. Multi-currency is a future change
  and would touch the `monto` schema and the dashboard math.
- Mobile is a future change. The web UI is responsive enough to
  work on a phone browser but is not optimized for it.
