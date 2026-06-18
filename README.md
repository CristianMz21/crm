# CRM (Django + DRF)

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF 3.17](https://img.shields.io/badge/DRF-3.17-red.svg)](https://www.django-rest-framework.org/)
[![Spec: spec-kit](https://img.shields.io/badge/spec-spec--kit-purple.svg)](https://github.com/github/spec-kit)
[![status: in progress](https://img.shields.io/badge/status-in%20progress-yellow.svg)]()
[![code style: ruff](https://img.shields.io/badge/code%20style-ruff-orange.svg)](https://docs.astral.sh/ruff/)

A real, productive CRM for solo salespeople and small teams. Built
by hand on Django 6 + Django REST Framework. Single-owner auth,
opportunities in a configurable pipeline, activities log, audit log,
advanced filtering, CSV export, and a dashboard with the metrics a
salesperson actually looks at.

> **¿Por qué AGPL-3.0?** Si alguien toma este código y lo hostea
> como servicio (SaaS), tiene que abrir el código de su servicio.
> Es la licencia que mejor protege el open source contra el cierre
> proprietário.

---

## Tabla de contenidos

- [¿Qué hace?](#qué-hace)
- [Quickstart](#quickstart)
- [Principios rectores](#principios-rectores)
- [Stack](#stack)
- [Documentación del proyecto](#documentación-del-proyecto)
- [Status](#status)
- [Estructura del repo](#estructura-del-repo)
- [Contribuir](#contribuir)
- [Seguridad](#seguridad)
- [Tests](#tests)
- [Licencia](#licencia)

---

## ¿Qué hace?

| Capacidad | Para qué |
|---|---|
| Auth de owner | Session auth con Django built-in. Un solo owner en v1, modelo listo para más. |
| Clientes + contactos | CRUD, búsqueda, filtros. Soft delete. |
| Pipeline con stages | Configurable. Default: Nuevo → En proceso → Ganado / Perdido. |
| Oportunidades | Monto en Decimal, asignación a usuario, cierre automático. |
| Bitácora de actividades | Llamadas, emails, reuniones contra cliente u oportunidad. |
| Audit log | Cada create/update/delete queda registrada con diff. |
| Filtros avanzados | `?ciudad=`, `?activo=`, `?monto__gte=`, `?etapa=`, `?search=`. |
| Export CSV streaming | `?format=csv` en cualquier endpoint de lista. |
| Dashboard | Pipeline por etapa, ganado/perdido del mes, win rate, top abiertos. |
| Saved searches | Guardar y ejecutar filtros compuestos. |

Detalle en [`specs/001-crm-mvp/spec.md`](./specs/001-crm-mvp/spec.md).

---

## Quickstart

```bash
git clone https://github.com/CristianMz21/crm.git
cd crm

python -m venv .venv
source .venv/bin/activate          # o .venv\Scripts\activate en Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python seed.py                     # opcional: 50 clientes fake

python manage.py runserver
```

Luego:

- Admin: <http://127.0.0.1:8000/admin/>
- API: <http://127.0.0.1:8000/api/>
- API root con browsable UI: misma URL, la DRF UI es la default

Guía extendida: [`specs/001-crm-mvp/quickstart.md`](./specs/001-crm-mvp/quickstart.md).

---

## Principios rectores

Estos 8 principios están en
[`.specify/memory/constitution.md`](./.specify/memory/constitution.md)
y son no negociables. Toda PR se valúa contra ellos.

1. **Spec-First** — no se escribe código sin un spec en `specs/`.
   El spec es el contrato; el código es su implementación.
2. **Hand-Written Code Only** — el código lo escribe un humano.
   La IA puede ayudar a investigar y explicar, no a tipear.
3. **Money is Decimal, Never Float** — `DecimalField` para
   `Oportunidad.monto`. `Decimal("100.50")` con string, jamás
   `Decimal(100.50)`.
4. **Soft Delete for Business Data** — los modelos de negocio
   tienen `activo`. Hard delete solo via acción admin explícita.
5. **ORM is Sacred — N+1 is a P0** — `select_related` para FK,
   `prefetch_related` para reverse FK y M2M. Cada lista y cada
   detalle tiene un `assertNumQueries` que lo bloquea.
6. **Validation at the Right Layer** — DB integrity en el modelo,
   field rules en `validate_<field>`, cross-field en `validate(self, attrs)`.
7. **No Silent Failures** — cada mutación deja un `AuditLog`,
   cada error devuelve JSON con `code` + `message`.
8. **Tests at the API Boundary** — `APIClient` para todo. Coverage
   real > coverage ficticio.

---

## Stack

| Componente | Versión | Para qué |
|---|---|---|
| Python | 3.11+ | Runtime |
| Django | 6.0 | Framework web + ORM + admin + auth |
| Django REST Framework | 3.17 | API REST, serializers, viewsets |
| django-filter | 24+ | Filtros declarativos |
| django-debug-toolbar | 4+ | Detectar N+1 en dev |
| pytest | 8+ | Test runner |
| pytest-django | 4.8+ | Integración pytest + Django |
| Faker | 25+ | Seed data |
| ruff | latest | Lint + format |
| SQLite | 3 | Default DB (Postgres-ready) |
| github/spec-kit | latest | Spec-driven development |

---

## Documentación del proyecto

El proyecto usa
[github/spec-kit](https://github.com/github/spec-kit). **No hay
carpeta `docs/` a propósito** — los artefactos spec-kit son la
única fuente de verdad.

| Artefacto | Para qué |
|---|---|
| [`.specify/memory/constitution.md`](./.specify/memory/constitution.md) | Los 8 principios no negociables. |
| [`specs/001-crm-mvp/spec.md`](./specs/001-crm-mvp/spec.md) | Spec del MVP: 8 user stories, 15 FRs, 7 success criteria. |
| [`specs/001-crm-mvp/data-model.md`](./specs/001-crm-mvp/data-model.md) | 9 entidades, campos, decisiones. |
| [`specs/001-crm-mvp/plan.md`](./specs/001-crm-mvp/plan.md) | Stack, arquitectura, estructura de apps. |
| [`specs/001-crm-mvp/research.md`](./specs/001-crm-mvp/research.md) | Por qué estas elecciones, qué se descartó. |
| [`specs/001-crm-mvp/tasks.md`](./specs/001-crm-mvp/tasks.md) | 150 tareas por user story. |
| [`specs/001-crm-mvp/quickstart.md`](./specs/001-crm-mvp/quickstart.md) | Cómo correr el sistema. |
| [`specs/001-crm-mvp/contracts/api.yaml`](./specs/001-crm-mvp/contracts/api.yaml) | OpenAPI 3 del contrato HTTP. |

**Regla de oro:** si cambia el comportamiento, cambia el spec.
Spec desactualizado = bug latente.

---

## Status

**El proyecto está en construcción.** El spec y el plan están
firmes; el código va por fases según
[`specs/001-crm-mvp/tasks.md`](./specs/001-crm-mvp/tasks.md).

| # | Historia | Prioridad | Estado |
|---|---|---|---|
| US1 | Auth (login, logout, sesión) | P1 (MVP) | ⬜ |
| US2 | Clientes + Contactos (CRUD, búsqueda, soft delete) | P1 (MVP) | 🔄 (modelos básicos) |
| US3 | Pipeline + Oportunidades + Dashboard | P1 (MVP) | ⬜ |
| US4 | Bitácora de actividades | P2 | ⬜ |
| US5 | Audit log endpoint + filtros | P2 | ⬜ |
| US6 | Export CSV streaming | P2 | ⬜ |
| US7 | Saved searches | P3 | ⬜ |
| US8 | Dashboard refinements | P3 | ⬜ |

**MVP = US1 + US2 + US3.** Cuando esos tres estén verdes, el CRM
ya es usable. Lo demás es valor incremental.

**Lo que ya hay en el repo** (no código MVP todavía):
- `clientes/models.py` con `Cliente` y `Contacto` en su forma
  básica (no la extendida del spec).
- Migraciones aplicadas.
- `clientes/admin.py` registrando `Cliente` y `Contacto`.
- Scaffolding de spec-kit completo.
- Spec, plan, data model, research, quickstart, tasks y OpenAPI
  contract escritos y revisables.

---

## Estructura del repo

```text
crm/
├── config/                          # proyecto Django (settings, urls, wsgi)
│
├── core/                            # infraestructura compartida
│   ├── models.py                    # abstract: TimeStampedModel, SoftDeleteModel, AuditModel
│   ├── managers.py                  # SoftDeleteManager
│   └── api/                         # BusquedaGuardada endpoint
│
├── clientes/                        # gestión de contactos: Cliente, Contacto, Etiqueta
│   ├── api/                         # capa DRF
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   ├── renderers.py            # CSV streaming
│   │   └── urls.py
│   ├── services/
│   ├── models.py
│   ├── managers.py
│   ├── signals.py
│   ├── admin.py
│   └── tests/
│
├── oportunidades/                   # pipeline de ventas: Oportunidad, Actividad
│   ├── api/
│   ├── services/
│   │   └── pipeline.py              # mover_etapa
│   ├── models.py
│   └── tests/
│
├── pipeline/                        # configuración de pipeline: Pipeline, Etapa
│   ├── api/
│   └── tests/
│
├── audit/                           # audit trail: AuditLog
│   ├── api/
│   └── tests/
│
├── dashboard/                       # analytics: sin modelos, solo endpoints
│   ├── services.py
│   └── tests/
│
├── templates/                       # HTML mínimo
│
├── conftest.py                      # fixtures pytest project-wide
│
├── .specify/                        # spec-kit
│   └── memory/constitution.md
│
├── specs/001-crm-mvp/               # spec del MVP
│
├── .github/                         # CI, issue templates, agents
│
├── seed.py
├── manage.py
├── pyproject.toml
└── LICENSE
```

---

## Contribuir

Por favor leé [`CONTRIBUTING.md`](./CONTRIBUTING.md) y la
[constitución](./.specify/memory/constitution.md) antes de abrir
un PR.

Resumen:

- **Spec primero.** El comportamiento vive en
  [`specs/001-crm-mvp/spec.md`](./specs/001-crm-mvp/spec.md). Si
  tu cambio modifica comportamiento, el spec se actualiza en el
  mismo PR.
- **Código a mano.** No se acepta código generado por IA
  (constitución principio II).
- **`pytest` verde** antes de pedir review.
- **Conventional Commits** en los mensajes. Sin
  `Co-Authored-By` de IA.
- **Ruff** para format y lint. Corre `ruff format . && ruff check .`
  antes de commit.

---

## Seguridad

Para reportar una vulnerabilidad, **NO abras un issue público**.
Mandá un mail o usá la opción de **Report a vulnerability** en la
pestaña "Security" del repositorio. Detalle en
[`SECURITY.md`](./SECURITY.md).

---

## Tests

```bash
pytest                           # toda la suite
pytest -k cliente                # los que matcheen "cliente"
pytest clientes/tests/test_orm.py # un archivo
pytest --lf                      # solo los que fallaron la última vez
pytest --cov=.                   # con cobertura
```

`python manage.py check` valida la configuración sin tocar la DB.

Tests de N+1 viven en
`clientes/tests/test_orm.py` con `CaptureQueriesContext` y
`assertNumQueries`. Son obligatorios para toda vista de lista o
detalle (constitución principio V).

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

Construido con [github/spec-kit](https://github.com/github/spec-kit)
para que la documentación no mienta y el código respete el spec.
