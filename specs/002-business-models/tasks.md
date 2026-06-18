# Tasks: 002-business-models

**Spec**: [spec.md](./spec.md) | **Ref**: [data-model.md](../000-architecture/data-model.md)

---

## S010 — Pipeline model

**File**: `pipeline/models.py`
**Spec ref**: data-model.md → pipeline.Pipeline

`Pipeline(TimeStampedModel)`: `nombre` (CharField 100, unique), `descripcion` (TextField blank), `es_default` (BooleanField default False). `__str__` → nombre. `Meta.ordering = ["nombre"]`.

**Verify**: `makemigrations pipeline` + `migrate` + `shell -c "from pipeline.models import Pipeline; print(Pipeline._meta.verbose_name)"` → `pipeline`
- [x] S010 done

---

## S011 — Etapa model

**File**: `pipeline/models.py`
**Spec ref**: data-model.md → pipeline.Etapa

`Etapa(TimeStampedModel)`: `pipeline` (FK Pipeline CASCADE related_name="etapas"), `nombre` (CharField 50), `orden` (PositiveIntegerField), `cerrada` (BooleanField default False), `es_ganado` (BooleanField default False), `color` (CharField 7 blank default ""). `Meta.ordering = ["pipeline", "orden"]`. `Meta.constraints = [UniqueConstraint(fields=["pipeline", "orden"], name="unique_orden_per_pipeline")]`. `__str__` → `f"{self.pipeline.nombre} > {self.nombre}"`.

**Verify**: `makemigrations pipeline` + `migrate`
- [x] S011 done

---

## S012 — AuditLog model

**File**: `audit/models.py`
**Spec ref**: data-model.md → audit.AuditLog

`AuditLog(Model)`: `actor` (FK User PROTECT null=True related_name="+"), `action` (CharField choices create/update/delete), `model` (CharField 80), `object_id` (PositiveBigIntegerField), `object_repr` (CharField 255), `changes` (JSONField default=dict), `timestamp` (DateTimeField auto_now_add db_index). `Meta.ordering = ["-timestamp"]`. `Meta.indexes = [Index(fields=["model", "object_id"])]`. `__str__` → `f"{self.action} {self.model}:{self.object_id}"`.

**Verify**: `makemigrations audit` + `migrate`
- [x] S012 done

---

## S013 — Update Cliente model

**File**: `clientes/models.py`
**Spec ref**: data-model.md → clientes.Cliente

Update existing `Cliente` to:
- Inherit `TimeStampedModel, SoftDeleteModel, AuditModel` (from `core.models`)
- Remove explicit `activo` and `fecha_creacion` (now inherited)
- Add: `pais` (CharField 80 blank default ""), `sitio_web` (URLField blank), `notas` (TextField blank)
- Add: `etiquetas` M2M to `Etiqueta`, related_name="clientes", blank=True
- Set `objects = SoftDeleteManager()` and `objects_all = Manager()` (from `core.managers`)
- Keep `__str__`, `get_absolute_url`, `Meta.ordering`

**Verify**: `makemigrations clientes` + `migrate` + `shell -c "from clientes.models import Cliente; print([f.name for f in Cliente._meta.get_fields()])"` → includes pais, sitio_web, notas, etiquetas, fecha_modificacion, creado_por
- [x] S013 done

---

## S014 — Etiqueta model

**File**: `clientes/models.py`
**Spec ref**: data-model.md → clientes.Etiqueta

`Etiqueta(TimeStampedModel)`: `nombre` (CharField 50 unique), `color` (CharField 7 blank default ""), `descripcion` (CharField 200 blank). `__str__` → nombre. `Meta.ordering = ["nombre"]`.

**Verify**: `makemigrations clientes` + `migrate`
- [x] S014 done

---

## S015 — Update Contacto model

**File**: `clientes/models.py`
**Spec ref**: data-model.md → clientes.Contacto

Update existing `Contacto` to:
- Inherit `TimeStampedModel, SoftDeleteModel, AuditModel`
- Add: `notas` (TextField blank)
- Set `objects = SoftDeleteManager()`, `objects_all = Manager()`
- Keep FK to Cliente, related_name="contactos", CASCADE

**Verify**: `makemigrations clientes` + `migrate`
- [x] S015 done

---

## S016 — Oportunidad model

**File**: `oportunidades/models.py`
**Spec ref**: data-model.md → oportunidades.Oportunidad

`Oportunidad(TimeStampedModel, SoftDeleteModel, AuditModel)`: `cliente` (FK `clientes.Cliente` PROTECT related_name="oportunidades"), `titulo` (CharField 200), `descripcion` (TextField blank), `monto` (DecimalField max_digits=14 decimal_places=2), `etapa` (FK `pipeline.Etapa` PROTECT related_name="oportunidades"), `asignado_a` (FK User PROTECT null=True blank=True related_name="oportunidades"), `fecha_cierre` (DateField null=True blank=True). `Meta.ordering = ["-fecha_creacion"]`. `__str__` → titulo. `objects = SoftDeleteManager()`, `objects_all = Manager()`.

**Verify**: `makemigrations oportunidades` + `migrate` + `shell -c "from oportunidades.models import Oportunidad; print(Oportunidad._meta.get_field('monto').__class__.__name__)"` → `DecimalField`
- [x] S016 done

---

## S017 — Actividad model

**File**: `oportunidades/models.py`
**Spec ref**: data-model.md → oportunidades.Actividad

`Actividad(TimeStampedModel, AuditModel)` — NO SoftDelete (activities are never deleted). `cliente` (FK `clientes.Cliente` CASCADE related_name="actividades"), `oportunidad` (FK `oportunidades.Oportunidad` SET_NULL null=True blank=True related_name="actividades"), `tipo` (CharField choices llamada/email/reunion), `nota` (TextField). `Meta.ordering = ["-fecha"]`. `__str__` → `f"{self.tipo}: {self.cliente.nombre}"`.

**Verify**: `makemigrations oportunidades` + `migrate`
- [x] S017 done

---

## S018 — BusquedaGuardada model

**File**: `core/models.py`
**Spec ref**: data-model.md → core.BusquedaGuardada

`BusquedaGuardada(Model)`: `nombre` (CharField 100), `endpoint` (CharField 100), `filtros` (JSONField default=dict), `creado_por` (FK User CASCADE related_name="busquedas_guardadas"). `Meta.unique_together = [("endpoint", "nombre", "creado_por")]`. `__str__` → nombre.

**Verify**: `makemigrations core` + `migrate`
- [x] S018 done

---

## S019 — Checkpoint

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run  # "No changes detected"
uv run python manage.py migrate
uv run ruff check core/ clientes/ oportunidades/ pipeline/ audit/
uv run ruff format --check core/ clientes/ oportunidades/ pipeline/ audit/
```

All pass → all 9 models ready.

- [x] S019 checkpoint passed ✅
