# Spec 004: Auth (US1)

**Branch**: `004-auth`
**Depends on**: 003-services-audit
**Blocks**: nothing (US2 and US3 can proceed in parallel)
**User story**: US1 — Authenticate and reach my dashboard (P1 MVP)

## What this delivers

Session-based authentication for the API. The owner can log in, log
out, and retrieve their user info. Unauthenticated requests to any
business endpoint get 403.

## Deliverables

- `AuthViewSet` with `me()`, `login()`, `logout()` actions
- Routes registered at `/api/auth/`
- Session cookie set on login, destroyed on logout

## Acceptance criteria

1. Unauthenticated GET `/api/auth/me/` → 403
2. Authenticated GET `/api/auth/me/` → 200 with `{id, username, email}`
3. POST `/api/auth/login/` with bad credentials → 400
4. POST `/api/auth/login/` with good credentials → 200, session cookie set
5. POST `/api/auth/logout/` → 200, session destroyed
6. After logout, GET `/api/auth/me/` → 403
7. `pytest` auth tests all pass
8. `ruff check .` passes

## Spec references

- [spec.md](../000-architecture/spec.md) → User Story 1
- [contracts/api.yaml](../000-architecture/contracts/api.yaml) → `/api/auth/*`
