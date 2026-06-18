# Proposal — CRM MVP (7-day training)

## Why

The user is preparing for a Django + DRF technical interview and is rebuilding
the same five-entity CRM from scratch as spaced repetition. The project
already has a written specification, but lacks:

- A single source of truth for **what the system does** (spec).
- A single source of truth for **how it is built** (design).
- A single source of truth for **what is left to do** (tasks).

Free-form documentation in `docs/` duplicated that information in 12 files
with overlap. This change consolidates everything into the OpenSpec artifact
format and removes the duplicated markdown.

## What changes

This change covers the full 7-day plan from the project specification:

1. **Day 1** — fundamentals, `Cliente` + `Contacto`, admin.
2. **Day 2** — vanilla views, URLs, templates.
3. **Day 3** — `Oportunidad`, `Actividad`, `Etiqueta`, Faker seed.
4. **Day 4** — DRF API: serializers, validations, viewsets, router, pagination, filters.
5. **Day 5** — ORM intensive: Q, annotate, aggregate, select_related, prefetch_related.
6. **Day 6** — pytest, custom manager, signal, `assertNumQueries`.
7. **Day 7** — 90-minute timed rebuild from clean state.

The output is a working CRM with:

- 5 models with documented relationships.
- Vanilla Django views for CRUD.
- A REST API at `/api/` with filtering and pagination.
- A seed script that populates 50 realistic clients.
- A test suite that proves the API and ORM contracts.
- A custom manager and one signal implemented correctly.
- A `assertNumQueries` test that locks in the N+1 fix from day 5.

## What is out of scope

- Authentication, permissions, JWT.
- Production deployment, Docker, CI.
- Frontend framework (React, htmx, etc.).
- Anything beyond the five entities in the spec.
- Database other than SQLite.
- Any AI-generated code (project rule).

## Capabilities

This change is split into one capability with seven sub-areas, all under the
`crm` domain:

- `models` — 5 entities and their relationships.
- `views-web` — vanilla Django CRUD.
- `api` — DRF layer (serializers, viewsets, router, filters, pagination).
- `seed` — Faker-based data population.
- `orm` — query patterns and the N+1 fix.
- `testing` — pytest setup, fixtures, contract tests.
- `manager-signal` — custom manager and one well-scoped signal.

Each sub-area corresponds to one day in the task list. The delta spec in
`specs/crm/spec.md` defines the contract for every sub-area.

## Approach

We follow the OpenSpec artifact flow:

1. `proposal.md` (this file) — intent and scope.
2. `specs/crm/spec.md` — observable behavior per capability.
3. `design.md` — architecture, decisions, ORM patterns, pitfalls.
4. `tasks.md` — one section per day, checkable items.
5. `verify-report.md` — written after tests pass.
6. Archive: move change folder to `changes/archive/2026-06-18-crm-mvp/`.

We do NOT use OpenSpec for daily implementation; we use it for **the change
as a whole**. Day-to-day code is hand-written by the user following the tasks.

## Risks

- **R1 (high) — Timeline slip:** the 7-day plan is ambitious. A single day
  slipping cascades. Mitigation: each day is independently shippable; skipping
  a day does not invalidate prior days.
- **R2 (medium) — N+1 not actually fixed:** easy to miss a relation. Mitigation:
  the `assertNumQueries` test in day 5 locks in the count.
- **R3 (medium) — Spec drift:** code may diverge from spec. Mitigation: verify
  phase compares each scenario against the actual implementation; failing
  scenarios block archive.
- **R4 (low) — Documentation bloat:** the previous `docs/` folder had 12 files
  with overlap. Mitigation: this change deletes `docs/` and keeps knowledge
  in the SDD artifacts only.

## Rollback

This is a greenfield project. There is no production state to roll back. The
"rollback" is `git reset` to before the change. The new `openspec/` and
`docs/` changes are isolated and reversible at the git level.

If mid-change a day's work is broken, that day's tasks can be reverted
without affecting other days, because tasks are grouped by day and the
project's atomicity is at the day level.
