# Sistema de Inventario FEFO - FruitMarket

## Descripción
Aplicación web desarrollada en Python con Flask para la gestión de inventarios de FruitMarket. El sistema utiliza el método FEFO (First Expired, First Out) para garantizar que los productos más próximos a caducar se utilicen o vendan primero, reduciendo el desperdicio.

## Características Principales
* Registro y control de inventario basado en fechas de caducidad.
* Clasificación por categorías de productos.
* Gestión de desperdicios.
* Base de datos local con SQLite.

## Tecnologías Utilizadas
* **Backend:** Python, Flask
* **Base de Datos:** SQLite 
* **Frontend:** HTML, CSS (Plantillas renderizadas)

## Instalación y Ejecución
1. Clona este repositorio.
2. Crea y activa un entorno virtual (venv).
3. Instala las dependencias: `pip install -r requirements.txt`
4. Ejecuta la aplicación: `python app.py`
5. Abre tu navegador web y dirígete a `http://127.0.0.1:5000`
