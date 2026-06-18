# Contributing

¡Gracias por tu interés en contribuir! Este documento te guía a través
del proceso y nuestras convenciones.

## TL;DR

1. Abrí un issue antes de un PR grande. Para fixes chicos, PR directo.
2. Fork + branch con prefijo (`feat/`, `fix/`, `docs/`, `refactor/`).
3. Código escrito a mano. **Nada de código generado por IA.**
4. Si cambia el comportamiento, cambiá el spec en `openspec/`.
5. `pytest` verde antes de pedir review.
6. PR con descripción que explique el por qué, no el qué.

---

## Regla de oro: spec antes que código

Este proyecto usa **OpenSpec/SDD**. El comportamiento del sistema vive en
`openspec/changes/crm-mvp/specs/crm/spec.md` (delta spec). Antes de
escribir código:

- Si tu cambio **agrega comportamiento** → agregá un `ADDED Requirement`
  al spec con escenarios Given/When/Then.
- Si tu cambio **modifica comportamiento** → agregá un `MODIFIED Requirement`.
- Si tu cambio **borra comportamiento** → agregá un `REMOVED Requirement`.
- Si el cambio es puramente interno (refactor sin cambio de
  comportamiento) → no hace falta tocar el spec, pero documentá el
  por qué en la descripción del PR.

El reviewer va a pedir el cambio de spec si el código cambia el
comportamiento sin actualizar el spec.

---

## Workflow de contribución

### 1. Issue primero (cambios grandes)

Para features nuevas, refactors grandes, o cambios de arquitectura,
abrí un issue primero. Esperá el OK antes de empezar a codear.

Para bugs y cambios chicos, podés ir directo al PR.

### 2. Fork + branch

```bash
git clone https://github.com/<tu-usuario>/crm.git
cd crm
git checkout -b feat/lo-que-estas-haciendo
```

Convención de prefijos:

- `feat/` — feature nueva
- `fix/` — bug fix
- `docs/` — solo documentación
- `refactor/` — refactor sin cambio de comportamiento
- `test/` — solo tests
- `chore/` — tareas de mantenimiento (deps, CI, etc.)

### 3. Escribí el código a mano

**No** se acepta código generado por IA (Copilot, Cursor, ChatGPT, etc.).
El proyecto es un ejercicio de práctica personal. Si te trabás con
sintaxis trivial, consultá la documentación oficial de Django/DRF.

### 4. Corré los tests

```bash
pytest
```

Todos los tests deben pasar antes de pedir review. Si agregaste
comportamiento nuevo, agregá tests que lo cubran.

### 5. Actualizá el spec

Si corresponde (ver "spec antes que código" arriba), modificá el
delta spec en `openspec/changes/crm-mvp/specs/crm/spec.md` y marcalos
tareas correspondientes en `openspec/changes/crm-mvp/tasks.md` con
`[x]`.

### 6. Commit + push

Mensajes de commit siguiendo [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(api): add filter by ciudad on ClienteViewSet
fix(models): make Contacto.cascade delete Cliente orphans
docs(openspec): mark day 2 tasks complete
test(orm): add assertNumQueries for cliente detail
refactor(views): extract form_valid in cliente_create
```

Sin Co-Authored-By de IA. Sin emoji. Mensajes en imperativo presente.

### 7. Pull request

Usá la [PR template](./.github/PULL_REQUEST_TEMPLATE.md). El reviewer
asignado va a:

- Verificar que el código está escrito a mano.
- Verificar que el spec está actualizado si corresponde.
- Correr `pytest`.
- Comentar sobre la implementación.

---

## Estilo de código

- PEP 8. Sin debates innecesarios.
- snake_case para funciones y variables.
- PascalCase para clases.
- Docstrings en funciones públicas no triviales.
- **No** comments que describan el código. Sí comments que expliquen
  el por qué (reglas de negocio, decisiones de performance, etc.).
- **No** `# noqa`, `# type: ignore`, etc. Si falla, arreglalo.

---

## Estructura del proyecto

```
crm/
├── config/              # proyecto Django (settings, urls, wsgi)
├── clientes/            # app principal
│   ├── api/             # capa DRF
│   ├── tests/           # tests
│   ├── managers.py      # custom manager
│   ├── signals.py       # signals
│   └── models.py
├── templates/           # templates vanilla Django
├── openspec/            # ← documentación y spec del proyecto
├── seed.py              # script de seed con Faker
├── manage.py
├── requirements.txt
└── pyproject.toml
```

---

## Reportar bugs

Usá el [bug report template](./.github/ISSUE_TEMPLATE/bug_report.md).
Incluí un ejemplo mínimo reproducible si podés.

---

## Proponer features

Usá el [feature request template](./.github/ISSUE_TEMPLATE/feature_request.md).
Explicá el problema que querés resolver, no la solución.

---

## Código de conducta

Por favor leé [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md). Aplican a
todas las interacciones del proyecto (issues, PRs, reviews, discusiones).

---

## Preguntas

Abrí un issue con la etiqueta `question`. No hay canal de chat todavía.

---

## Licencia

Al contribuir, aceptás que tu contribución se publique bajo la misma
licencia AGPL-3.0 del proyecto. Ver [`LICENSE`](./LICENSE).
