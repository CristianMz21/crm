# Tasks: 003-services-audit

**Spec**: [spec.md](./spec.md) | **Ref**: [data-model.md](../000-architecture/data-model.md) → D-5, D-7, D-8

---

## S020 — ensure_default_pipeline()

**File**: `oportunidades/services/pipeline.py`
**Spec ref**: data-model.md → D-7

Function that creates a default Pipeline (es_default=True) with 4 Etapas: Nuevo (orden=0), En proceso (orden=1), Ganado (orden=2, cerrada=True, es_ganado=True), Perdido (orden=3, cerrada=True). Idempotent.

**Verify**: `shell -c "from oportunidades.services.pipeline import ensure_default_pipeline; p = ensure_default_pipeline(); print(p.nombre, p.etapas.count())"` → `(name) 4`
- [x] S0020 done

---

## S021 — mover_etapa()

**File**: `oportunidades/services/pipeline.py`
**Spec ref**: data-model.md → D-8

`mover_etapa(oportunidad, etapa_id, *, actor=None)`: sets etapa, sets/clears fecha_cierre based on `cerrada`, calls `save()`. Raises `ValueError` if etapa belongs to different pipeline.

**Verify**: create oportunidad in Nuevo, move to Ganado, check `fecha_cierre is not None`
- [x] S0021 done

---

## S022 — log_action()

**File**: `audit/services/__init__.py`
**Spec ref**: data-model.md → audit.AuditLog

`log_action(*, actor, action, instance, changes)`: creates AuditLog with model=`instance.__class__._meta.label`, object_id=`instance.pk`, object_repr=`str(instance)`.

**Verify**: `shell -c "from audit.services import log_action; print(callable(log_action))"` → `True`
- [x] S0022 done

---

## S023 — compute_diff()

**File**: `audit/services/__init__.py`
**Spec ref**: data-model.md → D-5

`compute_diff(instance)`: re-fetches instance from DB, compares fields, returns `{field: {old, new}}` for changed fields. Excludes `fecha_creacion`, `fecha_modificacion`.

**Verify**: `shell -c "from audit.services import compute_diff; print(callable(compute_diff))"` → `True`
- [x] S0023 done

---

## S024 — post_save signals for audit

**Files**: `clientes/signals.py`, `oportunidades/signals.py`
**Spec ref**: data-model.md → D-5

`post_save` handlers for Cliente, Contacto, Etiqueta (in clientes) and Oportunidad, Actividad (in oportunidades). On `created=True`: log create. On `created=False`: compute_diff, if non-empty log update. Skip if `raw` or `instance._skip_audit`.

**Verify**: create a Cliente, check `AuditLog.objects.filter(model="clientes.Cliente").count()` → 1
- [x] S0024 done

---

## S025 — post_delete signals for audit

**Files**: `clientes/signals.py`, `oportunidades/signals.py`

`post_delete` handlers for same 5 models. Log delete with `changes={"old": model_to_dict(instance)}`.

**Verify**: hard-delete a Cliente via `objects_all`, check AuditLog has delete entry
- [x] S0025 done

---

## S026 — Register signals in apps.py:ready()

**Files**: `clientes/apps.py`, `oportunidades/apps.py`, `pipeline/apps.py`

`def ready(self): from . import signals  # noqa: F401`

**Verify**: `python manage.py check` → no AppRegistryNotReady
- [x] S0026 done

---

## S027 — pre_save signal: single default pipeline

**File**: `pipeline/signals.py`
**Spec ref**: data-model.md → D-7

`pre_save` on Pipeline: if `instance.es_default=True`, set `es_default=False` on all other pipelines.

**Verify**: create 2 pipelines with es_default=True, check only 1 has it
- [x] S0027 done

---

## S028 — Data migration: seed default pipeline

**File**: `oportunidades/migrations/0002_seed_default_pipeline.py`
**Spec ref**: plan.md → Migration strategy

Data migration calling `ensure_default_pipeline()` in `forwards()`. `reverse()` deletes the seeded pipeline.

**Verify**: `migrate` + `shell -c "from pipeline.models import Pipeline; print(Pipeline.objects.filter(es_default=True).count())"` → 1
- [x] S0028 done

---

## S029 — Admin registrations

**Files**: `clientes/admin.py`, `oportunidades/admin.py`, `pipeline/admin.py`, `audit/admin.py`, `core/admin.py`

Register every concrete model. Use `list_display`, `list_filter`, `search_fields`. AuditLog is read-only.

**Verify**: `python manage.py check` + visit `/admin/`
- [x] S0029 done

---

## S030 — Checkpoint

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py shell -c "
from oportunidades.services.pipeline import ensure_default_pipeline, mover_etapa
from audit.services import log_action, compute_diff
p = ensure_default_pipeline()
print(f'Pipeline: {p.nombre}, etapas: {p.etapas.count()}')
print('Foundation ready')
"
uv run ruff check .
uv run ruff format --check .
```

All pass → foundation complete. US1, US2, US3 can begin.

- [x] S030 foundation checkpoint passed ✅

---

## Validación Integral — Spec 003-services-audit

> **Obligatoria**: Esta sección debe completarse al 100% antes de considerar la spec lista para merge.

### Comandos de validación

```bash
# 1. Linting — sin errores ni advertencias
uv run ruff check core/ clientes/ oportunidades/ pipeline/ audit/
# Criterio: 0 errors, 0 warnings

# 2. Formateo — consistencia de código
uv run ruff format --check core/ clientes/ oportunidades/ pipeline/ audit/
# Criterio: "All files already formatted"

# 3. Supresiones — cero silencios
grep -rn "# type: ignore\|# noqa\|pragma: no cover\|cast(" \
  core/ clientes/ oportunidades/ pipeline/ audit/ --include='*.py'
# Criterio: 0 resultados

# 4. Tests unitarios
uv run pytest core/tests/ clientes/tests/ oportunidades/tests/ pipeline/tests/ audit/tests/ -v
# Criterio: todos pasan

# 5. Cobertura de código
uv run pytest core/tests/ clientes/tests/ oportunidades/tests/ pipeline/tests/ audit/tests/ \
  --cov=core --cov=clientes --cov=oportunidades --cov=pipeline --cov=audit \
  --cov-report=term-missing
# Criterio: ≥90% para código nuevo

# 6. Invariantes de negocio
uv run python manage.py shell -c "
from django.contrib.auth.models import User
from audit.models import AuditLog
from audit.services import log_action, compute_diff
from oportunidades.services.pipeline import ensure_default_pipeline, mover_etapa
from pipeline.models import Pipeline, Etapa
u = User.objects.create(username='val_s03', email='v3@t.com')
p1 = ensure_default_pipeline()
p2 = ensure_default_pipeline()
assert p1.pk == p2.pk, 'Debería ser idempotente'
assert p1.etapas.count() == 4
from clientes.models import Cliente
c = Cliente.objects.create(nombre='VC3', email='vc3@t.com', creado_por=u)
from oportunidades.models import Oportunidad
o = Oportunidad.objects.create(
    cliente=c, titulo='VO3', monto='500.00',
    etapa=p1.etapas.first(), creado_por=u
)
etapa_ganado = p1.etapas.get(es_ganado=True)
mover_etapa(o, etapa_ganado.id)
assert o.fecha_cierre is not None
etapa_nuevo = p1.etapas.get(orden=0)
mover_etapa(o, etapa_nuevo.id)
assert o.fecha_cierre is None
p_other = Pipeline.objects.create(nombre='Other')
e_other = Etapa.objects.create(pipeline=p_other, nombre='EO', orden=0)
try:
    mover_etapa(o, e_other.pk)
    assert False, 'Debería haber fallado'
except ValueError:
    pass
log_action(actor=u, action='create', instance=c, changes={'new': {'nombre': 'VC3'}})
assert AuditLog.objects.filter(model='clientes.Cliente').exists()
c.nombre = 'VC3 Modified'
diff = compute_diff(c)
assert 'nombre' in diff
assert diff['nombre']['old'] == 'VC3'
c2 = Cliente.objects.create(nombre='Sig', email='sig@t.com', creado_por=u)
assert AuditLog.objects.filter(model='clientes.Cliente', action='create').count() >= 1
print('✓ Todos los invariantes de negocio verificados')
"

# 7. Migraciones
uv run python manage.py makemigrations --check --dry-run
# Criterio: "No changes detected"

# 8. Regresiones
uv run python manage.py check
# Criterio: 0 issues
```

### Checklist de aceptación

- [ ] `ruff check` → 0 errores, 0 advertencias
- [ ] `ruff format --check` → todos los archivos formateados
- [ ] Cero supresiones en código
- [ ] Todos los tests unitarios pasan
- [ ] Cobertura ≥90% para código nuevo
- [ ] Invariantes de negocio verificados
- [ ] Migraciones sin cambios pendientes
- [ ] `manage.py check` → 0 issues
- [ ] No se introducen regresiones

**Estado**: ✅ Validación Integral completada
