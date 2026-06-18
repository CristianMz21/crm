# CRM Constitution

> Governing principles for the CRM project. Every spec, plan, and task
> is validated against this document. The constitution supersedes ad-hoc
> decisions and is amended only through documented, dated changes.

## Core Principles

### I. Spec-First (NON-NEGOTIABLE)

No code is written before a spec exists in `specs/`. Every change to
the system — feature, bugfix, refactor that alters behavior — lands in
a `spec.md` first, with user stories, functional requirements, and
success criteria. The spec is the contract. The code is the
implementation of that contract. When they disagree, the spec wins
until the spec is amended.

- A new feature requires a `specs/###-feature-name/spec.md` with at
  least one user story and acceptance scenarios.
- Bug fixes that reveal missing requirements MUST extend the spec in
  the same PR that fixes the bug.
- Refactors that do not change behavior do not need a spec change.
- The spec is reviewed before the code. PRs with code changes but no
  updated spec (when behavior changed) are rejected at review.

### II. Hand-Written Code Only

All application code is written by a human. AI tools may be used for
research, for explaining unfamiliar libraries, and for navigating
documentation, but the code that lands in this repository was typed
by a person. This is non-negotiable because the project is, at its
core, an exercise in recovering and retaining the muscle memory of
writing Django + DRF applications by hand.

- Pull requests containing AI-generated code are rejected at review.
- The constitution does not require labeling which lines were
  AI-assisted. It requires that the final code reflects deliberate
  human authorship, with the typical human artifacts: typos fixed,
  style consistent with neighboring code, comments that explain the
  "why" not the "what".

### III. Money is Decimal, Never Float

All monetary fields are `DecimalField` with explicit `max_digits` and
`decimal_places`. Arithmetic in Python uses `Decimal("...")` (string
construction) and never `Decimal(0.1)` (which silently preserves
float drift). The CRM does not lose centavos to IEEE 754.

- `Oportunidad.monto` is `DecimalField(max_digits=14, decimal_places=2)`.
- All `aggregate`/`annotate` results on monetary fields return `Decimal`.
- Tests that compare monetary values use `Decimal("...")`, not `float`.

### IV. Soft Delete for Business Data

Clientes, Oportunidades, Actividades, Contactos, and Etiquetas are
soft-deleted via an `activo` boolean (or `archivado` when soft delete
and active/inactive are different concerns). Hard delete is reserved
for system-level data cleanup and never for records the user created.
Foreign keys from other tables can point to archived rows; the
application layer is responsible for filtering them out of normal
queries.

- Hard delete is exposed only to administrators and only via a
  documented `delete_permanently` action, never via the standard
  `DELETE` endpoint.
- Archived records keep their foreign keys, audit log entries, and
  history intact.
- The default manager returns only non-archived records. A separate
  manager `objects_all` returns everything.

### V. ORM is Sacred — N+1 is a P0 Bug

Queries that fan out (1 + N) are a P0 bug, not a nit. Every endpoint
that returns a list or detail must use `select_related` for ForeignKey
and `prefetch_related` for reverse ForeignKey and ManyToMany. The
correctness of this is locked in by a regression test.

- Every list view has a test that asserts a bounded query count.
- Every detail view has a test that asserts a bounded query count.
- New `assertNumQueries` tests are required for any new view that
  returns more than one record.
- The Django Debug Toolbar is installed in development and used
  during code review when query count is in doubt.

### VI. Validation Lives at the Right Layer

- **Database integrity** (uniqueness, NOT NULL, FK existence) lives
  in the model via `unique=True`, `null=False`, `ForeignKey`.
- **Field-level business rules** (forbidden domain, format) live in
  the serializer's `validate_<field>` method.
- **Cross-field business rules** (X requires Y) live in the
  serializer's `validate(self, attrs)` method.
- The model's `clean()` is reserved for rules that apply even outside
  the API (e.g. admin, scripts). It is NOT relied upon by the API.
- A `CheckConstraint` at the DB level is the last resort, when a rule
  is so important it must hold even under direct SQL writes.

### VII. No Silent Failures

The system never silently swallows an error. Every failure path
produces a log line, an audit log entry, or a user-visible error
message. The bar is: when something goes wrong, you can find out
when, where, why, and what data was affected.

- Signals and background work log to `logging` and write to
  `AuditLog` when mutating business data.
- API errors return structured JSON with a `code` (machine-readable)
  and a `message` (human-readable). The HTTP status code matches
  the situation.
- Database-level exceptions (IntegrityError, DataError) are caught
  at the API boundary and translated to a 400 or 409 with a clear
  message — never a 500.

### VIII. Tests at the API Boundary, Not Implementation

Tests exercise the system through the public surface (DRF API client
+ Django test client). Internal helpers (services, querysets) are
covered indirectly through the API tests. The point of the test
suite is to lock in observable behavior, not to inflate coverage
metrics by importing every internal function.

- Every endpoint has at least one happy-path test and one
  failure-mode test.
- Every cross-field validation rule has a test that POSTs a request
  that should fail and asserts the 400 status and the error key.
- ORM tests use `assertNumQueries` to lock query counts.

## Quality Standards

- **PEP 8** for style. `ruff format` and `ruff check` run on every
  PR via CI.
- **Type hints** in function signatures for public APIs. Body
  type hints are not required but encouraged for non-trivial logic.
- **No suppressions.** No `# noqa`, `# type: ignore`, or
  `@pytest.mark.skip`. Errors are fixed, not silenced.
- **No dead code.** Unused imports, commented-out blocks, and
  unreachable branches are removed before commit.
- **Conventional Commits** for commit messages.
  `feat(scope):`, `fix(scope):`, `docs(scope):`, `refactor(scope):`,
  `test(scope):`, `chore(scope):`. No `Co-Authored-By` lines for
  AI assistants.

## Stack Constraints

- **Python 3.11+** (project currently on 3.13).
- **Django 5.x** (project on 6.0).
- **Django REST Framework** for the API.
- **django-filter** for declarative filtering.
- **SQLite** for development and tests. Production may move to
  PostgreSQL; the data layer must not depend on SQLite-specific
  behavior.
- **pytest + pytest-django** for tests. No `unittest.TestCase` from
  Django directly.
- **Faker** for seed data.
- **No Django REST Framework SimpleJWT, no dj-rest-auth, no AllAuth**
  in v1. Auth is the built-in Django auth with a custom login view
  and a `LoginRequiredMixin` / DRF `IsAuthenticated` permission.

## Development Workflow

- **Branch naming**: `###-short-name` where `###` is the spec
  number, mirroring `specs/###-short-name/`. `main` is always
  deployable.
- **PRs require**: spec impact assessment in the description,
  `pytest` green, `ruff` green, and a review from the maintainer.
- **Merging**: squash merge by default. The PR title becomes the
  commit subject on `main`.
- **Releases**: tagged on `main` after a meaningful batch of changes
  lands. Versioning follows SemVer: `MAJOR.MINOR.PATCH`.
- **Daily hygiene**: `git pull`, `pytest`, and a quick scan of
  `git log` before starting work. If a day's work doesn't end with
  green tests, the spec is not considered updated.

## Governance

- The constitution supersedes local conventions and ad-hoc decisions.
  When a member believes a principle is wrong, the right path is to
  propose an amendment, not to silently work around it.
- Amendments are committed as a change to this file, with the
  version bump and the date in the footer.
- The constitution is reviewed every quarter. If it stops reflecting
  the project's reality, it is amended.
- All PRs and reviews must verify compliance with the principles
  above. PRs that violate a principle without an explicit
  justification (and a corresponding amendment) are rejected.

**Version**: 1.0.0 | **Ratified**: 2026-06-18 | **Last Amended**: 2026-06-18
