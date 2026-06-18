---
name: Feature request
about: Proponer una nueva funcionalidad o cambio
title: "[FEAT] "
labels: ["enhancement"]
assignees: []
---

## Problema

¿Qué problema querés resolver? ¿A quién le duele? Ejemplos:

- "Como vendedor, quiero ver mis clientes ordenados por último contacto
  porque me ayuda a priorizar follow-ups."
- "Como admin, quiero exportar oportunidades a CSV porque necesito
  hacer reportes fuera del sistema."

## Solución propuesta

Una descripción clara de qué querés que pase. NO es un plan de
implementación — es el comportamiento esperado.

## Alternativas consideradas

¿Qué otras opciones miraste? Por qué esta es mejor.

## Spec impact

Si tu feature cambia el comportamiento del sistema, va a requerir
actualizar `openspec/changes/crm-mvp/specs/crm/spec.md`. Indicá:

- ¿Agrega un nuevo `ADDED Requirement`?
- ¿Modifica uno existente (`MODIFIED`)?
- ¿Borra alguno (`REMOVED`)?

Si no sabés, está bien. Lo discutimos en el issue.

## Criterios de aceptación

Lista de condiciones verificables que tiene que cumplir el cambio
para considerarse hecho. Ejemplos:

- [ ] `pytest` pasa.
- [ ] Existe un test que verifica el comportamiento nuevo.
- [ ] El delta spec en `openspec/` está actualizado.
- [ ] El README está actualizado (si aplica).

## Out of scope

Qué NO querés que entre en este cambio. Sirve para limitar el scope.

## Contexto adicional

Screenshots, mockups, referencias a otros proyectos, etc.
