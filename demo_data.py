"""Datos de ejemplo para la versión publicada (se cargan solo si no hay lotes)."""
import datetime

import database as db


def cargar_datos_demo():
    conn = db.get_db_connection()
    hay_lotes = conn.execute("SELECT COUNT(*) FROM Lote").fetchone()[0] > 0
    conn.close()
    if hay_lotes:
        return

    hoy = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).date()

    def hace(dias):
        return (hoy - datetime.timedelta(days=dias)).isoformat()

    cats = {
        'Cítricos': db.crear_categoria('Cítricos', 20, 0, 30.0, 4),
        'Berries': db.crear_categoria('Berries', 6, 1, 26.0, 2),
        'Tropicales': db.crear_categoria('Tropicales', 8, 1, 28.0, 3),
        'Manzanas y peras': db.crear_categoria('Manzanas y peras', 25, 0, 30.0, 5),
    }
    productos = {}
    for nombre, cat, temporada in [
        ('Naranja Valencia', 'Cítricos', 'Invierno'), ('Limón persa', 'Cítricos', 'Todo el año'),
        ('Fresa', 'Berries', 'Primavera'), ('Zarzamora', 'Berries', 'Verano'),
        ('Plátano Tabasco', 'Tropicales', 'Todo el año'), ('Mango Ataulfo', 'Tropicales', 'Primavera'),
        ('Manzana Gala', 'Manzanas y peras', 'Otoño'), ('Pera Bosc', 'Manzanas y peras', 'Otoño'),
    ]:
        productos[nombre] = db.crear_producto(nombre, cats[cat], temporada)
    for nombre, cantidad, dias in [
        ('Naranja Valencia', 120, 2), ('Naranja Valencia', 80, 15), ('Limón persa', 60, 5),
        ('Fresa', 25, 1), ('Fresa', 18, 4), ('Zarzamora', 12, 6), ('Plátano Tabasco', 90, 3),
        ('Plátano Tabasco', 40, 6), ('Mango Ataulfo', 50, 2), ('Manzana Gala', 150, 4),
        ('Manzana Gala', 70, 21), ('Pera Bosc', 45, 10),
    ]:
        db.crear_lote(productos[nombre], cantidad, hace(dias))
