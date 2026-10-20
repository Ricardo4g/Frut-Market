from database import calcular_dias_vida, calcular_estado_semaforo


def test_lote_con_muchos_dias_es_verde():
    assert calcular_estado_semaforo(10, tolerancia=3) == 'Verde'


def test_lote_dentro_de_tolerancia_es_amarillo():
    assert calcular_estado_semaforo(3, tolerancia=3) == 'Amarillo'


def test_lote_con_un_dia_es_rojo():
    assert calcular_estado_semaforo(1) == 'Rojo'


def test_lote_que_caduca_hoy_es_negro():
    assert calcular_estado_semaforo(0) == 'Negro'


def test_lote_caducado_es_negro():
    assert calcular_estado_semaforo(-2) == 'Negro'


def test_clima_caluroso_reduce_vida_util_30_por_ciento():
    assert calcular_dias_vida(10, 1, 30.0, temp_estimada=32.0, mes=5) == 7


def test_temporada_de_lluvias_reduce_vida_util_15_por_ciento():
    assert calcular_dias_vida(20, 1, 30.0, temp_estimada=22.0, mes=7) == 17


def test_categoria_no_sensible_conserva_vida_util():
    assert calcular_dias_vida(10, 0, 30.0, temp_estimada=35.0, mes=7) == 10
