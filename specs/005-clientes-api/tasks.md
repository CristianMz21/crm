# Tasks: 005-clientes-api

**Spec**: [spec.md](./spec.md) | **Ref**: [api.yaml](../000-architecture/contracts/api.yaml)

---

## S035 — ContactoSerializer

**File**: `clientes/api/serializers.py`

`ContactoSerializer(ModelSerializer)`: fields = id, nombre, cargo, email, telefono, notas, activo. read_only = [id].

- [ ] S035 done

---

## S036 — ClienteSerializer + ClienteDetailSerializer

**File**: `clientes/api/serializers.py`

`ClienteSerializer`: id, nombre, email, telefono, empresa, ciudad, pais, sitio_web, notas, activo, fecha_creacion, fecha_modificacion, etiquetas (list of names). `validate_email`: reject `@test.com`.

`ClienteDetailSerializer(ClienteSerializer)`: adds `contactos = ContactoSerializer(many=True, read_only=True)`.

- [ ] S036 done

---

## S037 — ClienteFilter

**File**: `clientes/api/filters.py`

`ClienteFilter(FilterSet)`: `ciudad` (exact), `activo` (BooleanFilter), `search` (CharFilter method → `Q(nombre__icontains) | Q(email__icontains)`).

- [ ] S037 done

---

## S038 — ClienteViewSet

**File**: `clientes/api/views.py`

`ModelViewSet`: queryset = `Cliente.objects.all()`, serializer_class = `ClienteSerializer`, filterset_class = `ClienteFilter`. `get_serializer_class()` → `ClienteDetailSerializer` for retrieve. `perform_destroy()` → soft delete (`activo=False`, `save()`).

- [ ] S038 done

---

## S039 — ContactoViewSet

**File**: `clientes/api/views.py`

`ModelViewSet` for `Contacto`. `get_queryset()` filters by `cliente_id` from URL kwargs.

- [ ] S039 done

---

## S040 — Register routes

**File**: `clientes/api/urls.py`

Register `ClienteViewSet` and `ContactoViewSet` in the router.

**Verify**: `python manage.py check`
- [ ] S040 done

---

## S041 — API tests

**File**: `clientes/tests/test_api_clientes.py`

13 tests: create 201, bad email 400, dup email 400, list paginated, filter ciudad, filter activo, search, detail with contactos, update, soft delete 204→404, nested contacto create, cascade on delete.

**Verify**: `uv run pytest clientes/tests/test_api_clientes.py -v` → 13 passed
- [ ] S041 done

---

## S042 — N+1 tests

**File**: `clientes/tests/test_orm.py`

`assertNumQueries` for: (1) list view constant queries, (2) detail view ≤ 5 queries (1 + prefetches).

**Verify**: `uv run pytest clientes/tests/test_orm.py -v` → 2 passed
- [ ] S042 done

---

## S043 — Audit tests

**File**: `clientes/tests/test_audit.py`

Tests: create produces audit log, update produces audit log with diff, delete produces audit log.

**Verify**: `uv run pytest clientes/tests/test_audit.py -v` → 3 passed
- [ ] S043 done

---

## S044 — Checkpoint

```bash
uv run pytest clientes/tests/ -v
uv run python manage.py check
uv run ruff check .
```

All pass → US2 done.

- [ ] S044 US2 checkpoint passed ✅
