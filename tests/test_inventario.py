import datetime

import database


def _hoy():
    return (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).date()


def test_login_correcto_y_incorrecto():
    assert database.login('admin', 'admin123')['rol'] == 'superuser'
    assert database.login('admin', 'contraseña_mala') is None


def test_salida_fefo_consume_primero_el_lote_mas_antiguo():
    id_cat = database.crear_categoria('Cítricos prueba', 30)
    id_prod = database.crear_producto('Naranja prueba', id_cat, 'Todo el año')
    antiguo = (_hoy() - datetime.timedelta(days=5)).isoformat()
    reciente = _hoy().isoformat()
    lote_reciente = database.crear_lote(id_prod, 10, reciente)
    lote_antiguo = database.crear_lote(id_prod, 10, antiguo)

    despachado = database.registrar_salida(id_prod, 12)

    conn = database.get_db_connection()
    cantidades = {r['id_lote']: r['cantidad_actual'] for r in conn.execute(
        "SELECT id_lote, cantidad_actual FROM Lote WHERE id_producto = ?", (id_prod,))}
    conn.close()
    assert despachado == 12
    assert cantidades[lote_antiguo] == 0
    assert cantidades[lote_reciente] == 8


def test_salida_sin_stock_no_despacha_nada():
    id_cat = database.crear_categoria('Vacía prueba', 10)
    id_prod = database.crear_producto('Sin stock', id_cat, 'Todo el año')
    assert database.registrar_salida(id_prod, 5) == 0
