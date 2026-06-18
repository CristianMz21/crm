---
name: Bug report
about: Reportar un comportamiento roto o inesperado
title: "[BUG] "
labels: ["bug"]
assignees: []
---

## Descripción

Una descripción clara y concisa del bug.

## Pasos para reproducir

1. Ir a '...'
2. Ejecutar '...'
3. Ver '...'
4. Esperar '...'

## Comportamiento esperado

Una descripción clara de qué esperabas que pase.

## Comportamiento actual

Qué pasa realmente. Si aplica, pegar el traceback completo.

```text
Traceback (most recent call last):
  ...
```

## Entorno

- OS: [ej. Ubuntu 24.04, macOS 15, Windows 11]
- Python: [ej. 3.13.1]
- Django: [ej. 6.0.6]
- DRF: [ej. 3.17.1]
- Forma de instalación: [venv, uv, poetry, docker, ...]

## Contexto adicional

Cualquier info relevante: screenshots, queries SQL generadas, número
de requests, links a issues relacionadas, etc.

## Checklist

- [ ] Busqué en los issues existentes para ver si ya fue reportado.
- [ ] El bug es reproducible con `python manage.py runserver` limpio.
- [ ] Si es un bug de ORM, incluí la query SQL (`print(qs.query)`).
- [ ] Si es un bug de API, incluí el método, URL, body y response.
