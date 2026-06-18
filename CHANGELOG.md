# Changelog

Todos los cambios notables a este proyecto se documentan acá. El formato
sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y este
proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Work in progress.** El proyecto está en día 1 de 7. Las versiones se
> publican cuando un día está completo y `pytest` pasa.

## [Unreleased]

### Added

- Spec-Driven Development con OpenSpec: `openspec/` con proposal, delta
  spec, design y tasks.
- Workflow de GitHub Actions: `pytest` en cada push y PR.
- Issue templates (bug, feature) y PR template.
- Dependabot para mantener dependencias actualizadas.

### Changed

- Documentación consolidada en `openspec/`. Eliminada carpeta `docs/`.

## [0.1.0] - 2026-06-18

### Added

- Estructura inicial del proyecto Django (`config/`, `clientes/`).
- Modelos `Cliente` y `Contacto` con sus migraciones.
- Admin de Django con `Cliente` y `Contacto` registrados.
- Repositorio público en GitHub con licencia AGPL-3.0.

### Notes

Este es el primer commit público. El proyecto está en día 1 de un
plan de 7 días (ver `openspec/changes/crm-mvp/tasks.md`).

[Unreleased]: https://github.com/CristianMz21/crm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/CristianMz21/crm/releases/tag/v0.1.0
