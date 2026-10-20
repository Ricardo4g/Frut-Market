def test_pagina_principal_responde(cliente):
    assert cliente.get('/').status_code == 200


def test_inventario_requiere_sesion(cliente):
    assert cliente.get('/api/inventario').status_code == 401


def test_login_invalido_es_rechazado(cliente):
    r = cliente.post('/api/login', json={'username': 'admin', 'password': 'x'})
    assert r.status_code == 401


def test_crear_categoria_y_consultar_inventario(cliente_autenticado):
    r = cliente_autenticado.post('/api/categorias', json={'nombre': 'Berries API', 'dias_vida_util': 5})
    assert r.status_code == 201
    r = cliente_autenticado.get('/api/inventario')
    assert r.status_code == 200
    assert 'inventario' in r.get_json()
