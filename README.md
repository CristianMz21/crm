# CRM de práctica (Django + DRF)

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF 3.17](https://img.shields.io/badge/DRF-3.17-red.svg)](https://www.django-rest-framework.org/)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-orange.svg)](https://peps.python.org/pep-0008/)
[![status: in progress](https://img.shields.io/badge/status-in%20progress-yellow.svg)]()

CRM mínimo hecho a mano como entrenamiento para una prueba técnica de
Django + DRF. Cinco entidades, API REST, ORM optimizado, tests con
`pytest`. **Todo el código se escribe a mano, sin IA.**

> **¿Por qué AGPL-3.0?** Si alguien toma este código y lo hostea como
> servicio (SaaS), tiene que abrir el código de su servicio. Es la
> licencia que mejor protege el open source contra el cierre proprietário.

---

## Tabla de contenidos

- [Características](#características)
- [Stack](#stack)
- [Quickstart](#quickstart)
- [Documentación](#documentación)
- [Roadmap de aprendizaje](#roadmap-de-aprendizaje)
- [Contribuir](#contribuir)
- [Seguridad](#seguridad)
- [Licencia](#licencia)
- [Autor](#autor)

---

## Características

- 5 modelos: `Cliente`, `Contacto`, `Oportunidad`, `Actividad`, `Etiqueta`.
- Admin de Django con todos los modelos registrados.
- API REST con DRF (serializers con validación, viewsets, router, paginación, filtros).
- Seed con Faker: 50 clientes con relaciones realistas.
- ORM optimizado: `select_related` + `prefetch_related` con test `assertNumQueries` que bloquea la regresión de N+1.
- Manager custom (`Cliente.activos`, `Cliente.con_oportunidades_ganadas`).
- Signal idempotente que crea una `Actividad` al cerrar un deal.
- Tests con `pytest` + `pytest-django`.
- Documentación manejada con **OpenSpec/SDD** dentro de `openspec/`.

---

## Stack

| Componente | Versión | Para qué |
|---|---|---|
| Python | 3.13+ | Runtime |
| Django | 6.0 | Framework web |
| Django REST Framework | 3.17 | API REST |
| django-filter | 24+ | Filtros declarativos |
| django-debug-toolbar | 4+ | Detectar N+1 |
| pytest | 8+ | Tests |
| pytest-django | 4.8+ | Integración pytest + Django |
| Faker | 25+ | Datos de seed |
| SQLite | 3 | Default DB |

---

## Quickstart

```bash
# 1. Clonar
git clone https://github.com/CristianMz21/crm.git
cd crm

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migrar
python manage.py migrate

# 5. Cargar datos de prueba
python seed.py

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Correr
python manage.py runserver
```

- Admin: <http://127.0.0.1:8000/admin/>
- API: <http://127.0.0.1:8000/api/>
- Tests: `pytest`

---

## Documentación

Toda la documentación del proyecto está manejada con **OpenSpec/SDD**
dentro de `openspec/`. **No hay carpeta `docs/` a propósito** — los
artefactos SDD son la única fuente de verdad.

| Artefacto | Para qué |
|---|---|
| [`openspec/config.yaml`](./openspec/config.yaml) | Reglas del proyecto, comandos de test/check. |
| [`openspec/specs/crm/spec.md`](./openspec/specs/crm/spec.md) | Spec principal (source of truth). |
| [`openspec/changes/crm-mvp/proposal.md`](./openspec/changes/crm-mvp/proposal.md) | Por qué y qué se construye. |
| [`openspec/changes/crm-mvp/specs/crm/spec.md`](./openspec/changes/crm-mvp/specs/crm/spec.md) | Delta spec con escenarios Given/When/Then. |
| [`openspec/changes/crm-mvp/design.md`](./openspec/changes/crm-mvp/design.md) | Arquitectura, decisiones, ORM patterns, pitfalls. |
| [`openspec/changes/crm-mvp/tasks.md`](./openspec/changes/crm-mvp/tasks.md) | Tareas por día (checkboxes). |
| [`openspec/changes/crm-mvp/state.yaml`](./openspec/changes/crm-mvp/state.yaml) | Estado del change (sobrevive compactaciones). |

**Regla de oro:** si cambia el comportamiento, cambia el spec. Spec
desactualizado = bug latente.

---

## Roadmap de aprendizaje

7 días, 1 capa por día. El detalle con checkboxes está en
[`openspec/changes/crm-mvp/tasks.md`](./openspec/changes/crm-mvp/tasks.md).

| Día | Capa | Spec coverage | Estado |
|---|---|---|---|
| 1 | Modelos `Cliente` + `Contacto` + admin | R-MODELS-01, R-MODELS-02 | ✅ |
| 2 | Vistas vanilla + templates | R-VIEWS-01..03 | ⬜ |
| 3 | `Oportunidad` + `Actividad` + `Etiqueta` + seed | R-MODELS-03..05, R-SEED-01 | ⬜ |
| 4 | API DRF (serializers, viewsets, validaciones) | R-API-01..04 | ⬜ |
| 5 | ORM intensivo + N+1 fix | R-ORM-01..03 | ⬜ |
| 6 | Tests + manager custom + signal | R-TEST-01..04, R-MGR-01..02, R-SIG-01 | ⬜ |
| 7 | Simulación a 90 minutos | — | ⬜ |

---

## Contribuir

Este proyecto acepta contribuciones. Por favor:

1. Leé [`CONTRIBUTING.md`](./CONTRIBUTING.md) antes de abrir un PR.
2. Pequeños cambios van con PR directo. Cambios grandes abren issue primero.
3. Todos los PRs deben pasar `pytest` antes de review.
4. El código se escribe a mano — **no se acepta código generado por IA**.
5. Spec antes que código. Si tu cambio cambia comportamiento, actualizá
   el spec en `openspec/`.

Por el código de conducta, mirá [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).

---

## Seguridad

Para reportar una vulnerabilidad, **NO abras un issue público**. Mandá un
mail o usá el canal de seguridad privada detallado en
[`SECURITY.md`](./SECURITY.md). Las vulnerabilidades confirmadas se
parchean dentro de las 48 horas.

---

## Tests

```bash
pytest                    # corre todo
pytest -k cliente         # corre los que matcheen "cliente"
pytest --lf               # solo los que fallaron la última vez
pytest --cov=clientes     # con cobertura
```

`python manage.py check` valida la configuración sin tocar la DB.

---

## Licencia

**AGPL-3.0** — ver [`LICENSE`](./LICENSE) para el texto completo.

En resumen: podés usar, modificar y distribuir el código, pero si
ponés una versión modificada en un servidor accesible por red, tenés
que publicar el código fuente de esa versión modificada. Es la
licencia que mejor protege el open source contra el uso proprietário
sin reciprocidad.

---

## Autor

**CristianMz21** — <https://github.com/CristianMz21>

Construido como proyecto de práctica para una prueba técnica de
Django + DRF. El código se escribe a mano siguiendo
[OpenSpec/SDD](https://github.com/FissionAI/OpenSpec) para
documentación que no mienta.

---

## Agradecimientos

- La comunidad de Django por la documentación oficial que es oro.
- El proyecto [OpenSpec](https://github.com/FissionAI/OpenSpec) por la
  metodología SDD.
- La FSF por mantener la AGPL viva.
