from flask import Flask, request, jsonify, render_template
from database import (inicializar_base_datos, inicializar_superusuario, login, 
                      actualizar_semaforo, crear_categoria, crear_producto, 
                      crear_lote, obtener_inventario, registrar_salida)
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configuración de la tarea programada
scheduler = BackgroundScheduler()
scheduler.add_job(actualizar_semaforo, 'cron', hour=0, minute=0)
scheduler.start()

# --- RUTAS DE INTERFAZ GRÁFICA (FRONTEND) ---
@app.route('/')
def inicio():
    # Carga la interfaz gráfica desde la carpeta templates
    return render_template('index.html')

# --- RUTAS DE LA API (BACKEND) ---
@app.route('/api/login', methods=['POST'])
def api_login():
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos:
        return jsonify({"error": "Faltan credenciales"}), 400
    usuario = login(datos['username'], datos['password'])
    if usuario:
        del usuario['password_hash']
        return jsonify({"mensaje": "Login exitoso", "usuario": usuario}), 200
    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/api/categorias', methods=['POST'])
def api_crear_categoria():
    datos = request.get_json()
    if not datos or 'nombre' not in datos or 'dias_vida_util' not in datos:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    id_cat = crear_categoria(datos['nombre'], datos['dias_vida_util'])
    return jsonify({"mensaje": "Categoría creada con éxito", "id_categoria": id_cat}), 201

@app.route('/api/productos', methods=['POST'])
def api_crear_producto():
    datos = request.get_json()
    if not datos or 'nombre' not in datos or 'id_categoria' not in datos:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    stock_min = datos.get('stock_minimo', 0) 
    id_prod = crear_producto(datos['nombre'], datos['id_categoria'], stock_min)
    return jsonify({"mensaje": "Producto creado con éxito", "id_producto": id_prod}), 201

@app.route('/api/lotes', methods=['POST'])
def api_crear_lote():
    datos = request.get_json()
    if not datos or 'id_producto' not in datos or 'cantidad' not in datos or 'fecha_ingreso' not in datos:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    id_lote = crear_lote(datos['id_producto'], datos['cantidad'], datos['fecha_ingreso'])
    return jsonify({"mensaje": "Lote registrado con éxito", "id_lote": id_lote}), 201

@app.route('/api/inventario', methods=['GET'])
def api_obtener_inventario():
    return jsonify({"inventario": obtener_inventario()}), 200

@app.route('/api/salidas', methods=['POST'])
def api_registrar_salida():
    datos = request.get_json()
    if not datos or 'id_producto' not in datos or 'cantidad' not in datos:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    
    despachado = registrar_salida(datos['id_producto'], datos['cantidad'])
    if despachado == 0:
        return jsonify({"error": "No hay stock disponible o vigente"}), 400
    return jsonify({"mensaje": f"Se despacharon {despachado} unidades exitosamente"}), 200

@app.route('/api/forzar_semaforo', methods=['POST'])
def api_forzar_semaforo():
    actualizar_semaforo()
    return jsonify({"mensaje": "Semáforo actualizado manualmente"}), 200

if __name__ == '__main__':
    inicializar_base_datos()
    inicializar_superusuario()
    app.run(debug=True, port=5000)