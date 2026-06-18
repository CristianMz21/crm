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
