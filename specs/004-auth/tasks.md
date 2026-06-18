# Tasks: 004-auth

**Spec**: [spec.md](./spec.md) | **Ref**: [api.yaml](../000-architecture/contracts/api.yaml) → `/api/auth/*`

---

## S031 — AuthViewSet

**File**: `core/api/views.py` (auth is cross-cutting, lives in core)
**Spec ref**: US1

`AuthViewSet(viewsets.ViewSet)` with:
- `me(request)` → `Response({"id", "username", "email"})` if authenticated, 403 if not
- `login(request)` → accepts `{username, password}`, calls `django.contrib.auth.authenticate` + `login`, returns 200 or 400
- `logout(request)` → calls `django.contrib.auth.logout`, returns 200

`@permission_classes([AllowAny])` on `login`, default `IsAuthenticated` on rest.

**Verify**: `shell -c "from core.api.views import AuthViewSet; print(AuthViewSet)"`
- [ ] S031 done

---

## S032 — Register routes

**File**: `core/api/urls.py`

```python
router.register("auth", AuthViewSet, basename="auth")
```

**Verify**: `python manage.py check` + `shell -c "from django.urls import reverse; print(reverse('auth-me'))"`
- [ ] S032 done

---

## S033 — Tests

**File**: `core/tests/test_api_auth.py`

Tests:
1. `test_unauthenticated_me_returns_403`
2. `test_authenticated_me_returns_200`
3. `test_login_bad_credentials_returns_400`
4. `test_login_good_credentials_returns_200`
5. `test_logout_clears_session`

Use `api_client` and `authenticated_client` fixtures from `conftest.py`.

**Verify**: `uv run pytest core/tests/test_api_auth.py -v` → 5 passed
- [ ] S033 done

---

## S034 — Checkpoint

```bash
uv run pytest core/tests/ -v
uv run python manage.py check
uv run ruff check .
```

All pass → US1 done. Owner can authenticate.

- [ ] S034 US1 checkpoint passed ✅
