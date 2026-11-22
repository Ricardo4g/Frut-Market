# Historial de versiones

## [1.1.0] - 2026-11-22
Actualización con monitoreo.

- Cada petición se registra en el log del servidor con método, ruta, código y tiempo de respuesta.
- Las peticiones de más de 1 segundo se marcan como WARNING y los errores 500 se registran con su detalle.
- Encabezados `X-Response-Time` y `X-App-Version` en todas las respuestas.
- `/health` ahora también reporta peticiones atendidas, errores 5xx, peticiones lentas y tiempo promedio.
- La versión se muestra en la interfaz, junto al usuario.

## [1.0.0] - 2026-11-22
Primera versión liberada con despliegue continuo a PythonAnywhere.

- Inventario FEFO con semáforo de caducidad (Óptimo, Próximo a vencer, Caducado).
- Login, categorías, productos, lotes, salidas FEFO y fundaciones.
- Integración continua con flake8 y pytest en GitHub Actions.
- Despliegue continuo a PythonAnywhere desde GitHub Actions: se publica solo cuando la CI pasa.
- Endpoint `/health` para revisar que el servicio y la base de datos estén disponibles.
