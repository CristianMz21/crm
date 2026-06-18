# Tasks: 007-dashboard

**Spec**: [spec.md](./spec.md) | **Ref**: [api.yaml](../000-architecture/contracts/api.yaml) → `/api/dashboard/`

---

## S056 — compute_dashboard_metrics()

**File**: `dashboard/services.py`

Function returning dict with:
- `pipeline_por_etapa`: list of `{etapa: {id, nombre}, total: str, cantidad: int}` via `Oportunidad.objects.values("etapa__id", "etapa__nombre").annotate(total=Sum("monto"), cantidad=Count("id")).filter(activo=True)`
- `ganado_mes_actual`: `Sum` of monto where `etapa__es_ganado=True` and `fecha_cierre__month=current, year=current`
- `perdido_mes_actual`: same for `es_ganado=False, cerrada=True`
- `win_rate`: `ganado / (ganado + perdido)` or 0
- `top_5_abiertos`: top 5 by monto where `etapa__cerrada=False`, `activo=True`

All Decimal values returned as strings.

**Verify**: `shell -c "from dashboard.services import compute_dashboard_metrics; print(compute_dashboard_metrics())"`
- [ ] S056 done

---

## S057 — DashboardView

**File**: `dashboard/api/views.py`

`APIView` with `get(request)` → `Response(compute_dashboard_metrics())`.

- [ ] S057 done

---

## S058 — Register dashboard route

**File**: `dashboard/api/urls.py`

`path("", DashboardView.as_view(), name="dashboard")`.

**Verify**: `python manage.py check`
- [ ] S058 done

---

## S059 — Tests

**File**: `dashboard/tests/test_dashboard.py`

5 tests:
1. `test_dashboard_devuelve_pipeline_por_etapa`
2. `test_dashboard_devuelve_ganado_y_perdido_del_mes`
3. `test_dashboard_sin_datos_devuelve_zero_no_500`
4. `test_dashboard_devuelve_top_5_abiertos`
5. `test_dashboard_win_rate`

**Verify**: `uv run pytest dashboard/tests/test_dashboard.py -v` → 5 passed
- [ ] S059 done

---

## S060 — MVP checkpoint 🎯

```bash
uv run pytest -v
uv run python manage.py check
uv run ruff check .
uv run ruff format --check .
```

All pass → **MVP IS DONE.** US1 + US2 + US3 deliver a working CRM.

Tag `v0.2.0` and ship.

- [ ] S060 MVP checkpoint passed 🎯🎯🎯
