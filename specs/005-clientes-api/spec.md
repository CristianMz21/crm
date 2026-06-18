# Spec 005: Clientes API (US2)

**Branch**: `005-clientes-api`
**Depends on**: 003-services-audit
**Blocks**: 006-oportunidades-api (Oportunidad FKs to Cliente)
**User story**: US2 — Manage clients and contacts (P1 MVP)

## What this delivers

Full CRUD API for `Cliente` and `Contacto` with search, filters,
soft delete, nested contacts in the detail view, and N+1-free
queries locked by `assertNumQueries`.

## Deliverables

- `ContactoSerializer`, `ClienteSerializer`, `ClienteDetailSerializer`
- `ClienteFilter` (ciudad, activo, search)
- `ClienteViewSet` (list, create, retrieve, update, soft-delete)
- `ContactoViewSet` (nested under cliente)
- `validate_email` rejecting `@test.com`
- Tests: 13 API tests + 2 N+1 tests + 3 audit tests

## Acceptance criteria

1. POST `/api/clientes/` with valid data → 201
2. POST with `@test.com` email → 400 with `email` error
3. POST with duplicate email → 400
4. GET `/api/clientes/` → paginated (25 per page)
5. GET `?ciudad=Cali` → only Cali clients
6. GET `?activo=false` → only inactive
7. GET `?search=acme` → case-insensitive on nombre + email
8. GET `/api/clientes/<id>/` → client + nested `contactos`
9. PATCH `/api/clientes/<id>/` → 200
10. DELETE `/api/clientes/<id>/` → 204 (soft delete), then GET → 404
11. POST `/api/clientes/<id>/contactos/` → 201
12. `assertNumQueries` on list view is constant regardless of N
13. `assertNumQueries` on detail view ≤ 5
14. Create/update/delete on Cliente produces AuditLog entries
15. `pytest` all pass + `ruff check .` passes

## Spec references

- [spec.md](../000-architecture/spec.md) → User Story 2
- [contracts/api.yaml](../000-architecture/contracts/api.yaml) → `/api/clientes/*`
- [data-model.md](../000-architecture/data-model.md) → clientes.Cliente, clientes.Contacto
- [constitution](../../.specify/memory/constitution.md) → principle V (N+1), VI (validation)
