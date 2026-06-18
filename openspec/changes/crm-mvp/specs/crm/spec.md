# Spec — CRM (delta)

This is the delta spec for the `crm` capability, added by change `crm-mvp`.
After archive, it merges into `openspec/specs/crm/spec.md`.

## Domain

`crm` — Customer Relationship Management training project.

---

## ADDED Requirements

### R-MODELS-01: Cliente entity

The system SHALL persist a `Cliente` with the following fields and constraints:

- `nombre` (string, max 150, required)
- `email` (email, required, unique across all Clientes)
- `telefono` (string, max 20, optional)
- `empresa` (string, max 150, optional)
- `ciudad` (string, max 100, optional, indexed for filtering)
- `activo` (bool, default true)
- `fecha_creacion` (datetime, set automatically on creation, immutable)

#### Scenarios

```gherkin
Given an empty database
When a Cliente is created with valid data
Then the Cliente is persisted
And __str__ returns the nombre

Given a Cliente with email "a@x.com" already exists
When another Cliente is created with email "a@x.com"
Then creation fails with an integrity error

Given Clientes exist with names "Berta" and "Ana"
When Cliente.objects.all() is iterated
Then the order is ["Ana", "Berta"] (ascending by nombre)
```

---

### R-MODELS-02: Contacto entity

The system SHALL persist a `Contacto` linked to exactly one `Cliente`.

- `cliente` (FK to Cliente, on_delete=CASCADE, related_name="contactos")
- `nombre` (string, max 150, required)
- `cargo` (string, max 100, optional)
- `email` (email, optional)
- `telefono` (string, max 20, optional)

#### Scenarios

```gherkin
Given a Cliente "ACME" exists
When a Contacto is created for ACME
Then cliente.contactos.count() == 1

Given a Cliente with 2 Contactos
When the Cliente is deleted
Then both Contactos are also deleted (CASCADE)

Given Cliente "ACME" with Contacto "Juan"
When str(contacto) is evaluated
Then it contains both "Juan" and "ACME"
```

---

### R-MODELS-03: Oportunidad entity

The system SHALL persist an `Oportunidad` (deal) linked to a `Cliente`.

- `cliente` (FK, on_delete=CASCADE, related_name="oportunidades")
- `titulo` (string, max 200, required)
- `monto` (Decimal, 12 digits, 2 decimal places, required)
- `estado` (choice: nuevo, en_proceso, ganado, perdido; default required)
- `fecha_cierre` (date, nullable)
- `fecha_creacion` (datetime, auto on create)

#### Scenarios

```gherkin
Given a Cliente exists
When an Oportunidad is created with monto "1000.50"
Then the stored monto equals Decimal("1000.50") exactly (no float drift)
```

---

### R-MODELS-04: Actividad entity

The system SHALL persist an `Actividad` (interaction log) linked to a `Cliente`.

- `cliente` (FK, on_delete=CASCADE, related_name="actividades")
- `tipo` (choice: llamada, email, reunion)
- `nota` (text, required, no max length)
- `fecha` (datetime, auto on create)

---

### R-MODELS-05: Etiqueta entity and M2M

The system SHALL persist an `Etiqueta` (tag) and a many-to-many relation with Cliente.

- `nombre` (string, max 50, unique, required)
- M2M with Cliente, related_name="etiquetas"

#### Scenarios

```gherkin
Given Etiqueta "vip" exists
When a Cliente is created and "vip" is added via cliente.etiquetas.add(etiqueta)
Then etiqueta.clientes.count() == 1
And cliente.etiquetas.first().nombre == "vip"
```

---

### R-VIEWS-01: Cliente list view

The system SHALL expose a GET endpoint at `/clientes/` that renders an HTML
table of all Clientes ordered by nombre.

#### Scenarios

```gherkin
Given 3 Clientes exist
When a GET request is made to /clientes/
Then response status is 200
And the response body contains all 3 client names
```

---

### R-VIEWS-02: Cliente detail view

The system SHALL expose a GET endpoint at `/clientes/<pk>/` that renders the
Cliente and its Contactos.

#### Scenarios

```gherkin
Given Cliente "ACME" with 2 Contactos exists
When a GET request is made to /clientes/<pk>/
Then response status is 200
And the body shows "ACME"
And the body shows both Contacto names
```

---

### R-VIEWS-03: Cliente create form

The system SHALL expose GET and POST endpoints at `/clientes/nuevo/` for
creating a Cliente via a ModelForm.

#### Scenarios

```gherkin
Given a GET to /clientes/nuevo/
Then response status is 200
And the body contains an HTML form with email and nombre inputs

Given a POST to /clientes/nuevo/ with valid data
Then a Cliente is created in the database
And response redirects to /clientes/<pk>/

Given a POST to /clientes/nuevo/ with duplicate email
Then response status is 200 (form re-rendered with errors)
And no Cliente is created
```

---

### R-API-01: Cliente list endpoint

The system SHALL expose `GET /api/clientes/` returning a paginated JSON list
of Clientes.

#### Scenarios

```gherkin
Given 15 Clientes exist
When a GET request is made to /api/clientes/
Then response status is 200
And response body is {"count": 15, "next": ..., "previous": ..., "results": [...]}
And results contains at most 10 items (PAGE_SIZE)

Given 5 Clientes in city "Cali" and 10 in "Bogota"
When a GET is made to /api/clientes/?ciudad=Cali
Then response body count is 5

Given Clientes with activo true and false
When a GET is made to /api/clientes/?activo=false
Then only inactive Clientes are returned
```

---

### R-API-02: Cliente detail endpoint with nested Contactos

The system SHALL expose `GET /api/clientes/<pk>/` returning the Cliente with
its Contactos nested as a read-only array.

#### Scenarios

```gherkin
Given Cliente "ACME" with 2 Contactos
When a GET is made to /api/clientes/<pk>/
Then response contains "contactos"
And contactos has 2 items
And each contacto has id, nombre, cargo, email, telefono

Given a non-existent pk
When a GET is made to /api/clientes/<pk>/
Then response status is 404
```

---

### R-API-03: Cliente create endpoint

The system SHALL expose `POST /api/clientes/` for creating a Cliente.

#### Scenarios

```gherkin
Given a POST to /api/clientes/ with valid JSON
Then response status is 201
And the Cliente exists in the database

Given a POST with email "tester@test.com"
Then response status is 400
And response body has key "email" with an error message

Given a POST with missing required field "nombre"
Then response status is 400
And response body has key "nombre" with an error message
```

---

### R-API-04: Oportunidad validation cross-field

The system SHALL reject an Oportunidad with `estado=ganado` and no
`fecha_cierre` with HTTP 400.

#### Scenarios

```gherkin
Given a Cliente exists
When a POST to /api/oportunidades/ with estado="ganado" and no fecha_cierre
Then response status is 400
And response body has key "fecha_cierre" with an error message

Given the same POST but with estado="en_proceso"
Then response status is 201

Given the same POST but with estado="ganado" AND fecha_cierre set
Then response status is 201
```

---

### R-SEED-01: Seed creates 50 clients with relations

Running `python seed.py` SHALL create exactly 50 Clientes, each with 1-4
Contactos, 0-3 Oportunidades, 0-5 Actividades, and 1-3 Etiquetas from a pool
of 8.

#### Scenarios

```gherkin
Given an empty database
When python seed.py is executed
Then Cliente.objects.count() == 50
And every Cliente has between 1 and 4 Contactos
And every Cliente has between 0 and 3 Oportunidades
And every Cliente has between 0 and 5 Actividades
And every Cliente has between 1 and 3 Etiquetas
And there are exactly 8 distinct Etiqueta rows
```

---

### R-ORM-01: OR with Q

The system SHALL provide a way to filter Clientes where `activo=true AND
ciudad="Cali"`, OR with at least one Oportunidad in estado="ganado".

#### Scenarios

```gherkin
Given Cliente "A" (activo, Cali, no oportunidades) and Cliente "B" (inactivo, Bogota, oportunidad ganada)
When Cliente.objects.filter(Q(activo=True, ciudad="Cali") | Q(oportunidades__estado="ganado")).distinct() is evaluated
Then both A and B are in the result
And no Cliente is duplicated
```

---

### R-ORM-02: Total ganado aggregation

The system SHALL compute the total `monto` of all Oportunidades with
estado="ganado" in a single query.

#### Scenarios

```gherkin
Given 3 Oportunidades: 1000 ganado, 500 ganado, 200 perdido
When Oportunidad.objects.filter(estado="ganado").aggregate(total=Sum("monto")) is evaluated
Then result is {"total": Decimal("1500.00")}
```

---

### R-ORM-03: Cliente detail with no N+1

The Cliente detail endpoint SHALL fetch the Cliente plus all related
Contactos, Oportunidades, Actividades, and Etiquetas in a bounded number
of queries regardless of how many relations exist.

#### Scenarios

```gherkin
Given a Cliente with 4 Contactos, 3 Oportunidades, 5 Actividades, 2 Etiquetas
When the detail view is rendered
Then assertNumQueries is less than or equal to 5 (1 for Cliente + 1 per prefetch)
And the response renders all relations
```

---

### R-TEST-01: Cliente.__str__ returns nombre

`pytest` SHALL include a test that asserts `str(cliente) == cliente.nombre`.

---

### R-TEST-02: Email unique constraint

`pytest` SHALL include a test that creating two Clientes with the same
email raises IntegrityError.

---

### R-TEST-03: API rejects forbidden domain

`pytest` SHALL include a test that POST to `/api/clientes/` with email
`"x@test.com"` returns 400 and contains "email" in the error body.

---

### R-TEST-04: API rejects opportunity ganada sin fecha

`pytest` SHALL include a test that POST to `/api/oportunidades/` with
`estado="ganado"` and no `fecha_cierre` returns 400 with key
`"fecha_cierre"`.

---

### R-MGR-01: Cliente.activos()

The `Cliente` model SHALL expose a `activos()` queryset method returning
only Clientes with `activo=True`.

#### Scenarios

```gherkin
Given 2 active and 1 inactive Cliente
When Cliente.activos.all() is evaluated
Then exactly 2 Clientes are returned
And the inactive one is not in the result
```

---

### R-MGR-02: Cliente.con_oportunidades_ganadas()

The `Cliente` model SHALL expose a `con_oportunidades_ganadas()` queryset
method returning distinct Clientes that have at least one Oportunidad with
`estado="ganado"`.

---

### R-SIG-01: Actividad auto on oportunidad ganada

When an Oportunidad with `estado="ganado"` is saved (created OR updated),
the system SHALL ensure an Actividad of tipo="llamada" exists for the
Oportunidad's Cliente, with nota referencing the Oportunidad titulo.

#### Scenarios

```gherkin
Given a Cliente exists
When an Oportunidad is created with estado="ganado"
Then an Actividad exists for that Cliente with tipo="llamada"
And the nota references the Oportunidad titulo

Given an existing Oportunidad with estado="en_proceso"
When the Oportunidad is updated to estado="ganado"
Then an Actividad is created (or already exists) for the Cliente
And the Actividad is not duplicated if save() is called twice
```

---

### R-VERIFY-01: All scenarios pass

The change is ready to archive when:

- All `pytest` tests pass.
- `python manage.py check` returns no issues.
- The verify report lists every delta spec scenario with verdict
  COMPLIANT or EXPLICITLY UNTESTED (with reason).
