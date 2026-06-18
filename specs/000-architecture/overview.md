# CRM MVP — Architecture & Roadmap

> **This is the project-level reference.** It holds the cross-cutting
> docs that all feature specs depend on. It is NOT a feature itself.
> Each feature spec in `specs/001-*` through `specs/007-*` references
> the docs here.

## Reference documents

| Doc | Purpose |
|---|---|
| [spec.md](./spec.md) | Full project spec: 8 user stories, 15 FRs, 7 success criteria. The source of truth for WHAT. |
| [plan.md](./plan.md) | Stack, architecture, project structure. The source of truth for HOW. |
| [data-model.md](./data-model.md) | All 9 entities, fields, relationships, decisions. Updated when any model changes. |
| [research.md](./research.md) | Tech stack rationale, alternatives considered, tradeoffs. |
| [quickstart.md](./quickstart.md) | How to get the system running from clean clone. |
| [contracts/api.yaml](./contracts/api.yaml) | OpenAPI 3 spec of the full API surface. |
| [adr-001-bounded-context-apps.md](./adr-001-bounded-context-apps.md) | ADR: why 6 apps, not 4. |

## Feature specs (execution order)

Each spec is a deliverable increment. Small enough to complete in one
sitting. Independent enough to test on its own.

| # | Spec | Delivers | Steps | Blocks | Status |
|---|---|---|---|---|---|
| 001 | [core-foundation](../001-core-foundation/) | Abstract models + soft delete manager | 5 | ALL | ⬜ |
| 002 | [business-models](../002-business-models/) | 7 concrete models + migrations | 10 | 003+ | ⬜ |
| 003 | [services-audit](../003-services-audit/) | Services, signals, admin, seed | 11 | 004+ | ⬜ |
| 004 | [auth](../004-auth/) | US1: login, logout, me endpoint | 4 | nothing | ⬜ |
| 005 | [clientes-api](../005-clientes-api/) | US2: Cliente + Contacto CRUD API | 10 | nothing | ⬜ |
| 006 | [oportunidades-api](../006-oportunidades-api/) | US3a: Pipeline + Oportunidad API | 12 | 005 | ⬜ |
| 007 | [dashboard](../007-dashboard/) | US3b: Dashboard metrics | 5 | 006 | ⬜ |

**MVP = 001 + 002 + 003 + 004 + 005 + 006 + 007** (57 steps total)

## Dependency graph

```
001-core-foundation
    └──► 002-business-models
              └──► 003-services-audit
                        ├──► 004-auth        ──► (MVP auth ready)
                        ├──► 005-clientes-api ──► (MVP clientes ready)
                        │         └──► 006-oportunidades-api
                        │                   └──► 007-dashboard
                        │                          └──► 🎯 MVP DONE
                        └──► (post-MVP: US4-US8)
```

## Post-MVP (deferred)

| US | Spec (future) | Priority |
|---|---|---|
| US4 | 008-actividades | P2 |
| US5 | 009-audit-api | P2 |
| US6 | 010-csv-export | P2 |
| US7 | 011-saved-searches | P3 |
| US8 | 012-dashboard-refinements | P3 |

These are listed for planning only. Do NOT start until 007-dashboard
passes its checkpoint.

## Constitution

All specs are governed by
[`.specify/memory/constitution.md`](../../.specify/memory/constitution.md).
The 8 principles are non-negotiable. Every PR is validated against them.
