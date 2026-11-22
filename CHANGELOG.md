# Historial de versiones

## [1.0.0] - 2026-11-22
Primera versión liberada con despliegue continuo a PythonAnywhere.

- Inventario FEFO con semáforo de caducidad (Óptimo, Próximo a vencer, Caducado).
- Login, categorías, productos, lotes, salidas FEFO y fundaciones.
- Integración continua con flake8 y pytest en GitHub Actions.
- Despliegue continuo a PythonAnywhere desde GitHub Actions: se publica solo cuando la CI pasa.
- Endpoint `/health` para revisar que el servicio y la base de datos estén disponibles.
