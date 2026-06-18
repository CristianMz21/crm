# CRM (Django + DRF)

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![DRF 3.17](https://img.shields.io/badge/DRF-3.17-red.svg)](https://www.django-rest-framework.org/)
[![Spec: spec-kit](https://img.shields.io/badge/spec-spec--kit-purple.svg)](https://github.com/github/spec-kit)
[![status: in progress](https://img.shields.io/badge/status-in%20progress-yellow.svg)]()

A real, productive CRM for solo salespeople and small teams. Built
by hand on Django + DRF. Single-owner auth, pipeline with stages,
opportunities with assignment, activities log, audit log, advanced
filtering, CSV export, dashboard with metrics, and a test suite
that locks the contracts.

> **¿Por qué AGPL-3.0?** Si alguien toma este código y lo hostea
> como servicio (SaaS), tiene que abrir el código de su servicio.
> Es la licencia que mejor protege el open source contra el cierre
> proprietário.

---

## Tabla de contenidos

- [Quickstart](#quickstart)
- [Documentación del proyecto](#documentación-del-proyecto)
- [Stack](#stack)
- [Status](#status)
- [Estructura](#estructura)
- [Contribuir](#contribuir)
- [Seguridad](#seguridad)
- [Licencia](#licencia)
- [Autor](#autor)

---

## Quickstart

```bash
git clone https://github.com/CristianMz21/crm.git
cd crm
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Detalle en [`specs/001-crm-mvp/quickstart.md`](./specs/001-crm-mvp/quickstart.md).

---

## Documentación del proyecto

Este proyecto usa **Spec-Driven Development** con
[github/spec-kit](https://github.com/github/spec-kit). **No hay
carpeta `docs/` a propósito** — los artefactos spec-kit son la
única fuente de verdad.

| Artefacto | Para qué |
|---|---|
| [`.specify/memory/constitution.md`](./.specify/memory/constitution.md) | Principios rectores del proyecto. |
| [`specs/001-crm-mvp/spec.md`](./specs/001-crm-mvp/spec.md) | Spec del MVP: user stories, FRs, success criteria. |
| [`specs/001-crm-mvp/plan.md`](./specs/001-crm-mvp/plan.md) | Stack, arquitectura, estructura. |
| [`specs/001-crm-mvp/data-model.md`](./specs/001-crm-mvp/data-model.md) | Entidades, campos, decisiones. |
| [`specs/001-crm-mvp/research.md`](./specs/001-crm-mvp/research.md) | Por qué estas elecciones, qué se descartó. |
| [`specs/001-crm-mvp/quickstart.md`](./specs/001-crm-mvp/quickstart.md) | Cómo correr el sistema. |
| [`specs/001-crm-mvp/tasks.md`](./specs/001-crm-mvp/tasks.md) | Tareas por user story. |
| [`specs/001-crm-mvp/contracts/api.yaml`](./specs/001-crm-mvp/contracts/api.yaml) | OpenAPI 3 del contrato HTTP. |

**Regla de oro:** si cambia el comportamiento, cambia el spec. Spec
desactualizado = bug latente.

---

## Stack

| Componente | Versión | Para qué |
|---|---|---|
| Python | 3.11+ | Runtime |
| Django | 6.0 | Framework web |
| Django REST Framework | 3.17 | API REST |
| django-filter | 24+ | Filtros declarativos |
| django-debug-toolbar | 4+ | Detectar N+1 |
| pytest | 8+ | Tests |
| pytest-django | 4.8+ | Integración pytest + Django |
| Faker | 25+ | Datos de seed |
| SQLite | 3 | Default DB |
| Spec Kit | latest | Spec-driven development |

---

## Status

El proyecto está en construcción. Día 1 del modelo Cliente + Contacto
ya está hecho. El resto sigue el plan en
[`specs/001-crm-mvp/tasks.md`](./specs/001-crm-mvp/tasks.md).

**MVP (P1)**: Auth + Clientes + Oportunidades en pipeline.
**P2**: Activities + Audit log + CSV export.
**P3**: Saved searches + refinamientos de dashboard.

| Capa | Spec | Status |
|---|---|---|
| Auth (US1) | [spec.md#user-story-1](./specs/001-crm-mvp/spec.md#user-story-1---authenticate-and-reach-my-dashboard-priority-p1) | ⬜ |
| Clientes + Contactos (US2) | [spec.md#user-story-2](./specs/001-crm-mvp/spec.md#user-story-2---manage-clients-and-contacts-priority-p1) | ⬜ |
| Pipeline + Oportunidades (US3) | [spec.md#user-story-3](./specs/001-crm-mvp/spec.md#user-story-3---move-opportunities-through-a-pipeline-priority-p1) | ⬜ |
| Activities (US4) | [spec.md#user-story-4](./specs/001-crm-mvp/spec.md#user-story-4---log-activities-against-clients-and-opportunities-priority-p2) | ⬜ |
| Audit log (US5) | [spec.md#user-story-5](./specs/001-crm-mvp/spec.md#user-story-5---audit-log-on-every-change-priority-p2) | ⬜ |
| CSV export (US6) | [spec.md#user-story-6](./specs/001-crm-mvp/spec.md#user-story-6---export-any-list-to-csv-priority-p2) | ⬜ |
| Saved searches (US7) | [spec.md#user-story-7](./specs/001-crm-mvp/spec.md#user-story-7---advanced-filtering-and-saved-searches-priority-p3) | ⬜ |
| Dashboard (US8) | [spec.md#user-story-8](./specs/001-crm-mvp/spec.md#user-story-8---dashboard-with-basic-metrics-priority-p3) | ⬜ |

---

## Estructura

```
crm/
├── config/                  # proyecto Django (settings, urls, wsgi)
├── clientes/                # Clientes, Contactos, Oportunidades, Activities, Etiquetas
├── pipeline/                # Pipeline + Etapas
├── audit/                   # Audit log
├── dashboard/               # Endpoint de dashboard
├── templates/               # Templates HTML mínimos
├── .specify/                # Configuración de spec-kit
│   └── memory/
│       └── constitution.md  # Principios rectores
├── specs/                   # Specs por feature
│   └── 001-crm-mvp/
│       ├── spec.md
│       ├── plan.md
│       ├── data-model.md
│       ├── research.md
│       ├── quickstart.md
│       ├── tasks.md
│       └── contracts/
│           └── api.yaml
├── seed.py                  # Seeder con Faker
├── manage.py
├── requirements.txt
└── pyproject.toml
```

---

## Contribuir

Por favor leé [`CONTRIBUTING.md`](./CONTRIBUTING.md) y
[`.specify/memory/constitution.md`](./.specify/memory/constitution.md)
antes de abrir un PR.

Resumen:

- Spec primero. El comportamiento vive en
  [`specs/001-crm-mvp/spec.md`](./specs/001-crm-mvp/spec.md).
- Código a mano. **No se acepta código generado por IA.**
- `pytest` verde antes de pedir review.
- Conventional Commits para los mensajes.
- Sin `Co-Authored-By` de IA.

---

## Seguridad

Para reportar una vulnerabilidad, **NO abras un issue público**.
Mandá un mail o usá la opción de **Report a vulnerability** en la
pestaña "Security" del repositorio. Detalle en
[`SECURITY.md`](./SECURITY.md).

---

## Tests

```bash
pytest                    # toda la suite
pytest -k cliente         # los que matcheen "cliente"
pytest --lf               # solo los que fallaron la última vez
pytest --cov=clientes     # con cobertura
```

`python manage.py check` valida la configuración sin tocar la DB.

---

## Licencia

**AGPL-3.0** — ver [`LICENSE`](./LICENSE) para el texto completo.

---

## Autor

**CristianMz21** — <https://github.com/CristianMz21>

Construido como proyecto real con
[github/spec-kit](https://github.com/github/spec-kit) para
documentación que no miente.
