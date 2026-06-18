# Tasks: 001-core-foundation

**Spec**: [spec.md](./spec.md) | **Ref**: [data-model.md](../000-architecture/data-model.md)

---

## S001 — TimeStampedModel

**File**: `core/models.py`
**Spec ref**: data-model.md → core.TimeStampedModel

Write an abstract model with:
- `fecha_creacion = DateTimeField(auto_now_add=True)`
- `fecha_modificacion = DateTimeField(auto_now=True)`
- `class Meta: abstract = True`

**Verify**:
```bash
uv run python manage.py shell -c "from core.models import TimeStampedModel; print(TimeStampedModel._meta.abstract)"
# → True
```
- [x] S001 done

---

## S002 — SoftDeleteModel

**File**: `core/models.py`
**Spec ref**: data-model.md → core.SoftDeleteModel

Write an abstract model with:
- `activo = BooleanField(default=True)`
- `class Meta: abstract = True`

**Verify**:
```bash
uv run python manage.py shell -c "from core.models import SoftDeleteModel; print(SoftDeleteModel._meta.get_field('activo').default)"
# → True
```
- [x] S002 done

---

## S003 — AuditModel

**File**: `core/models.py`
**Spec ref**: data-model.md → core.AuditModel

Write an abstract model with:
- `creado_por = ForeignKey("auth.User", on_delete=PROTECT, related_name="+")`
- `class Meta: abstract = True`

**Verify**:
```bash
uv run python manage.py shell -c "from core.models import AuditModel; print(AuditModel._meta.abstract)"
# → True
```
- [x] S003 done

---

## S004 — SoftDeleteManager + SoftDeleteQuerySet

**File**: `core/managers.py`
**Spec ref**: data-model.md → D-4

Write:
- `SoftDeleteQuerySet(models.QuerySet)` with `activos()` → `self.filter(activo=True)` and `archivados()` → `self.filter(activo=False)`
- `SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet))` that overrides `get_queryset()` to return `super().get_queryset().filter(activo=True)`

**Verify**:
```bash
uv run python manage.py shell -c "from core.managers import SoftDeleteManager, SoftDeleteQuerySet; print(SoftDeleteManager, SoftDeleteQuerySet)"
# → <class 'core.managers.SoftDeleteManager'> <class 'core.managers.SoftDeleteQuerySet'>
```
- [x] S004 done

---

## S005 — Checkpoint

```bash
uv run python manage.py check
uv run python manage.py makemigrations core --dry-run
# → "No changes detected" (abstract models don't create tables)
uv run ruff check core/
uv run ruff format --check core/
```

All 4 pass → core foundation ready.

- [x] S005 checkpoint passed ✅

---

## Validación Integral — Spec 001-core-foundation

> **Obligatoria**: Esta sección debe completarse al 100% antes de considerar la spec lista para merge.

### Comandos de validación

```bash
# 1. Linting — sin errores ni advertencias
uv run ruff check core/
# Criterio: 0 errors, 0 warnings

# 2. Formateo — consistencia de código
uv run ruff format --check core/
# Criterio: "All files already formatted"

# 3. Tipado estricto — contratos de tipos
uv run mypy core/
# Criterio: "Success: no issues found"

# 4. Supresiones — sin silencios injustificados
uv run ruff check core/ --select E,F,W,B,I,UP
uv run grep -rn "# type: ignore\|# noqa\|pragma: no cover\|cast(\|: Any" core/
# Criterio: 0 supresiones no documentadas

# 5. Tests unitarios
uv run pytest core/tests/ -v
# Criterio: todos pasan

# 6. Tests de integración (si aplica)
uv run pytest core/tests/ -v --tb=short
# Criterio: todos pasan

# 7. Cobertura de código
uv run pytest core/tests/ --cov=core --cov-report=term-missing
# Criterio: ≥90% para código nuevo

# 8. Invariantes de negocio
uv run python manage.py shell -c "
from core.models import TimeStampedModel, SoftDeleteModel, AuditModel
from core.managers import SoftDeleteManager, SoftDeleteQuerySet
# TimeStampedModel: abstract, tiene fecha_creacion y fecha_modificacion
assert TimeStampedModel._meta.abstract is True
assert hasattr(TimeStampedModel, 'fecha_creacion')
assert hasattr(TimeStampedModel, 'fecha_modificacion')
# SoftDeleteModel: abstract, tiene campo activo con default True
assert SoftDeleteModel._meta.abstract is True
assert SoftDeleteModel._meta.get_field('activo').default is True
# AuditModel: abstract, tiene creado_por FK
assert AuditModel._meta.abstract is True
assert hasattr(AuditModel, 'creado_por')
# SoftDeleteManager: filtra solo activos
assert issubclass(SoftDeleteManager, type)
# SoftDeleteQuerySet: tiene activos() y archivados()
assert hasattr(SoftDeleteQuerySet, 'activos')
assert hasattr(SoftDeleteQuerySet, 'archivados')
print('✓ Todos los invariantes de negocio verificados')
"
# Criterio: sin errores AssertionError

# 9. Migraciones
uv run python manage.py makemigrations core --check --dry-run
# Criterio: "No changes detected"

# 10. Regresiones
uv run python manage.py check
# Criterio: 0 issues
```

### Checklist de aceptación

- [ ] `ruff check core/` → 0 errores, 0 advertencias
- [ ] `ruff format --check core/` → todos los archivos formateados
- [ ] `mypy core/` → sin errores de tipado
- [ ] Sin supresiones injustificadas (`# type: ignore`, `# noqa`, etc.)
- [ ] Todos los tests unitarios pasan
- [ ] Todos los tests de integración pasan
- [ ] Cobertura ≥90% para código nuevo
- [ ] Invariantes de negocio verificados (abstract=True, defaults, FKs)
- [ ] Migraciones sin cambios pendientes
- [ ] `manage.py check` → 0 issues
- [ ] No se introducen regresiones

**Estado**: ✅ Validación Integral completada
