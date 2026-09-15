# Flujo de trabajo con Git

## Organización de ramas

El proyecto LexCore utiliza ramas para mantener organizado el desarrollo colaborativo.

Las ramas principales son:

- `main`: contiene la versión estable del proyecto.
- `dev`: se utiliza para integrar los cambios realizados durante el desarrollo.
- `feature/*`: corresponde a las ramas individuales utilizadas por los integrantes del equipo.

## Flujo de trabajo

Cada integrante desarrolla sus cambios en una rama independiente creada a partir de `dev`.

El flujo utilizado es:

```text
feature/integrante
        ↓
       dev
        ↓
       main
