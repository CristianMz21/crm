# Security Policy

## Reporting a Vulnerability

**No abras un issue público para reportar una vulnerabilidad.** Las
vulnerabilidades reportadas públicamente pueden ser explotadas antes de
que haya un fix disponible.

Mandá un mail a la dirección del maintainer listada en el perfil de
GitHub del proyecto, o usá la opción de **Report a vulnerability** en
la pestaña "Security" del repositorio de GitHub.

Incluí:

- Descripción de la vulnerabilidad.
- Pasos para reproducirla.
- Impacto potencial (qué se puede hacer con ella).
- Versión afectada.
- Tu nombre / handle si querés ser acreditado en el fix.

## Response timeline

- **Acknowledgement**: dentro de 48 horas.
- **Initial assessment**: dentro de 7 días.
- **Patch release**: según severidad:
  - Crítica: ASAP, usualmente < 7 días.
  - Alta: < 30 días.
  - Media/baja: según el roadmap.

Te mantendremos informado durante el proceso. Si la vulnerabilidad es
aceptada, te acreditamos en el release notes (a menos que prefieras
anonimato).

## Supported versions

Este proyecto está en desarrollo activo pero pre-release. Las versiones
con fixes de seguridad se determinan caso por caso. Por ahora,
actualizá a `main`.

| Versión | Soporte |
|---|---|
| `main` | ✅ |
| tags publicados | hasta el próximo release |

## Scope

El proyecto es un CRM de práctica. No hay datos reales de usuarios, no
hay auth en producción, no hay infraestructura expuesta. El "scope" de
seguridad es:

- **In scope**: bugs en el código que un atacante con acceso al código
  o al admin podría explotar. Por ejemplo, una validación rota que
  permite SQL injection o bypass de auth.
- **Out of scope**: ataques a la infraestructura de GitHub, denegación
  de servicio a nivel red, o ingeniería social contra maintainers.

## Política de disclosure

Seguimos **coordinated disclosure**:

1. Reportás en privado.
2. Investigamos y desarrollamos el fix.
3. Te avisamos cuando el fix está listo.
4. Publicamos el fix y un advisory al mismo tiempo.
5. Damos crédito al reporter (si quiere).

Por favor no disclosures públicos antes de que el fix esté disponible.
Si no respondemos en 30 días, podés disclosure público.

## Reconocimientos

Agradecemos a quienes reportan vulnerabilidades de forma responsable.
Las personas que contribuyen con reportes válidos son listadas en los
release notes (a menos que prefieran anonimato).
