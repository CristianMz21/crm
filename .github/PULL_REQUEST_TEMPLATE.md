## Resumen

<!-- Una o dos frases. ¿Qué hace este PR y por qué? -->

## Spec

<!-- ¿Cómo impacta este PR al spec? Marcá lo que aplique. -->

- [ ] No cambia comportamiento (refactor, chore, docs).
- [ ] Cambia comportamiento → actualicé `openspec/changes/crm-mvp/specs/crm/spec.md` con un `ADDED`, `MODIFIED`, o `REMOVED Requirement`.
- [ ] Cumple los escenarios del spec. Listá los IDs: R-XXX-XX, R-XXX-XX.

## Cambios

<!-- Lista de archivos modificados con una línea por archivo. -->

- `clientes/models.py` — agregué modelo `Oportunidad` con FK a `Cliente`.
- `clientes/api/serializers.py` — `OportunidadSerializer` con validación cross-field.
- `clientes/tests/test_api.py` — test del 400 cuando `estado=ganado` sin `fecha_cierre`.

## Cómo probar

<!-- Pasos concretos para que el reviewer verifique el cambio. -->

```bash
python manage.py migrate
python seed.py
pytest clientes/tests/test_api.py::test_oportunidad_ganada_sin_fecha_cierre_falla
```

## Checklist

- [ ] El código está escrito a mano (no generado por IA).
- [ ] `pytest` corre verde localmente.
- [ ] `python manage.py check` no reporta issues.
- [ ] Si agregué un modelo, las migraciones están commiteadas.
- [ ] Si agregué un endpoint, hay un test para él.
- [ ] Si el PR cambia comportamiento, el spec está actualizado.
- [ ] Si el PR toca ORM, consideré si necesita `assertNumQueries`.
- [ ] Mensajes de commit siguen Conventional Commits.
- [ ] El PR tiene un título descriptivo (no "fix" o "update").

## Screenshots / output

<!-- Si aplica, screenshots, output de tests, etc. -->

```text
============================= test session starts ==============================
...
```

## Notas para el reviewer

<!-- Lo que querés que el reviewer sepa: decisiones, tradeoffs, links. -->
