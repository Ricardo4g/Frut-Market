import os
import sys
import tempfile

# La base de datos de pruebas se crea en una carpeta temporal antes de importar la app
os.environ['DB_PATH'] = os.path.join(tempfile.mkdtemp(), 'test_inventario.db')
os.environ['DESACTIVAR_SCHEDULER'] = '1'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import app as app_module  # noqa: E402


@pytest.fixture
def cliente():
    app_module.app.config['TESTING'] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture
def cliente_autenticado(cliente):
    cliente.post('/api/login', json={'username': 'admin', 'password': 'admin123'})
    return cliente
