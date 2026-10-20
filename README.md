# Frut Market – Sistema de Inventario FEFO

![CI](https://github.com/Ricardo4g/Frut-Market/actions/workflows/main.yml/badge.svg)

## Objetivo
Gestionar el inventario de frutas y verduras de Frut Market con el método **FEFO**
(*First Expired, First Out*): los lotes más próximos a caducar se despachan primero,
lo que reduce la merma. Un semáforo (Verde, Amarillo, Rojo y Negro) indica el estado
de cada lote y se ajusta según el clima estimado de Aguascalientes.

## Funcionalidades
* Inicio de sesión con contraseña cifrada.
* Alta y baja de categorías (vida útil, sensibilidad al clima, tolerancia).
* Alta y baja de productos y registro de lotes por fecha de ingreso.
* Salidas de inventario que consumen primero el lote más antiguo (FEFO).
* Semáforo de caducidad recalculado automáticamente cada día.
* Registro de fundaciones o aliados para donar productos próximos a caducar.

## Herramientas utilizadas
| Herramienta | Uso |
|---|---|
| Python 3.12 | Lenguaje de programación |
| Flask 3.1 | Servidor web y API REST |
| SQLite | Base de datos local |
| APScheduler | Tarea diaria del semáforo |
| HTML / CSS / JavaScript | Interfaz (`templates/index.html`) |
| pytest | Pruebas automatizadas |
| flake8 | Verificación de sintaxis |
| Git y GitHub | Control de versiones |
| GitHub Actions | Integración continua |

## Estructura del proyecto
```
Frut-Market/
├── .github/workflows/main.yml   # Flujo de integración continua
├── app.py                       # Rutas de Flask y API
├── database.py                  # Base de datos y lógica FEFO
├── templates/index.html         # Interfaz web
├── static/logo.jpeg             # Logotipo
├── tests/                       # Pruebas con pytest
├── requirements.txt             # Dependencias de la aplicación
└── requirements-dev.txt         # Dependencias de desarrollo (pytest, flake8)
```

## Instrucciones de ejecución
1. Clona el repositorio:
   `git clone https://github.com/Ricardo4g/Frut-Market.git`
2. Crea y activa un entorno virtual:
   * Windows: `python -m venv venv` y luego `venv\Scripts\activate`
   * Linux/macOS: `python3 -m venv venv` y luego `source venv/bin/activate`
3. Instala las dependencias: `pip install -r requirements-dev.txt`
4. Ejecuta la aplicación: `python app.py`
5. Abre `http://127.0.0.1:5000` e inicia sesión con el usuario de prueba `admin` / `admin123`.

La base de datos `inventario.db` se crea automáticamente la primera vez.

## Pruebas e integración continua
Para ejecutar las validaciones de forma local:
```
flake8 . --exclude=venv --count --select=E9,F63,F7,F82 --show-source --statistics
python -m pytest -v
```
Cada `push` al repositorio ejecuta el flujo **Integracion Continua FEFO** en GitHub
Actions, que instala las dependencias, verifica la sintaxis con flake8 y ejecuta las
pruebas con pytest. Si alguna validación falla, el flujo se marca en rojo.
