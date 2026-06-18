# Changelog

Todos los cambios notables a este proyecto se documentan acá. El formato
sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y este
proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Pivot:** el proyecto dejó de ser un CRM de práctica de 7 días para
> convertirse en un CRM productivo real, manejado con
> [github/spec-kit](https://github.com/github/spec-kit). El plan de 7
> días en `openspec/` se eliminó. El nuevo plan vive en
> `specs/001-crm-mvp/tasks.md`.

## [Unreleased]

### Changed

- **Pivot a spec-kit.** La estructura de documentación pasó de
  OpenSpec (`openspec/`) a spec-kit (`.specify/` + `specs/`). El
  artefacto raíz ahora es la **constitución** (principios rectores),
  no el proposal.
- **Alcance ampliado.** El proyecto ya no es un ejercicio de 7 días.
  Es un CRM productivo real: auth, pipeline con etapas reales,
  asignación, audit log, export CSV, dashboard, saved searches.
  Scope detallado en `specs/001-crm-mvp/spec.md`.
- **Modelos ampliados.** Se agregan `Oportunidad`, `Actividad`,
  `Etiqueta`, `Pipeline`, `Etapa`, `AuditLog`, `BusquedaGuardada`.
  `Cliente` y `Contacto` se extienden con campos nuevos
  (`pais`, `sitio_web`, `notas`, `creado_por`).
- **Soft delete explícito.** Todos los modelos de negocio tienen
  `activo` y un manager custom que filtra por defecto.
- **Audit log automático.** Cada create/update/delete en modelos de
  negocio escribe a `AuditLog` vía signal.
- **API como contrato.** El spec HTTP completo vive en
  `specs/001-crm-mvp/contracts/api.yaml` (OpenAPI 3). Los tests
  `assertNumQueries` son obligatorios para toda vista de lista y
  detalle.

## [0.1.0] - 2026-06-18

### Added

- Estructura inicial del proyecto Django (`config/`, `clientes/`).
- Modelos `Cliente` y `Contacto` con sus migraciones.
- Admin de Django con `Cliente` y `Contacto` registrados.
- Repositorio público en GitHub con licencia AGPL-3.0.
- Scaffolding de OSS (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY,
  CHANGELOG, issue templates, PR template, CI workflows, dependabot,
  CODEOWNERS).
- Estructura OpenSpec (pre-pivot, ahora eliminada).

[Unreleased]: https://github.com/CristianMz21/crm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/CristianMz21/crm/releases/tag/v0.1.0
