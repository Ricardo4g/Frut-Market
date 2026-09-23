import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from database import (inicializar_base_datos, inicializar_superusuario, login, 
                      actualizar_semaforo, crear_categoria, eliminar_categoria,
                      crear_producto, eliminar_producto, crear_lote, obtener_inventario, 
                      obtener_resumen_general, registrar_salida, get_db_connection)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'frutmarket_secret_key_ultra_segura_2026')

inicializar_base_datos()
inicializar_superusuario()

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(actualizar_semaforo, 'cron', hour=0, minute=0)
    scheduler.start()
except Exception:
    pass

def verificar_autenticacion():
    return 'usuario' in session

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    datos = request.get_json()
    if not datos or 'username' not in datos or 'password' not in datos:
        return jsonify({"error": "Ingresa usuario y contraseña"}), 400
    
    usuario = login(datos['username'], datos['password'])
    if usuario:
        del usuario['password_hash']
        session['usuario'] = usuario['username']
        session['rol'] = usuario['rol']
        return jsonify({"mensaje": "Bienvenido a Frut Market", "usuario": usuario}), 200
    return jsonify({"error": "Credenciales inválidas. Acceso denegado."}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200

@app.route('/api/check_session', methods=['GET'])
def api_check_session():
    if verificar_autenticacion():
        return jsonify({"autenticado": True, "usuario": session.get('usuario')}), 200
    return jsonify({"autenticado": False}), 200

@app.route('/api/inventario', methods=['GET'])
def api_obtener_inventario():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    return jsonify({"inventario": obtener_inventario()}), 200

@app.route('/api/resumen_general', methods=['GET'])
def api_resumen_general():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    return jsonify({"resumen": obtener_resumen_general()}), 200

@app.route('/api/categorias', methods=['GET'])
def api_lista_categorias():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    conn = get_db_connection()
    cats = conn.execute("SELECT * FROM Categoria").fetchall()
    conn.close()
    return jsonify([dict(row) for row in cats])

@app.route('/api/categorias', methods=['POST'])
def api_crear_categoria():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    datos = request.get_json()
    if not datos or not datos.get('nombre') or not datos.get('dias_vida_util'):
        return jsonify({"error": "Faltan campos"}), 400
    sensible = 1 if datos.get('sensible_al_clima') else 0
    temp_umbral = float(datos.get('temp_umbral', 30.0))
    id_cat = crear_categoria(datos['nombre'], datos['dias_vida_util'], sensible, temp_umbral)
    return jsonify({"mensaje": "Categoría creada", "id_categoria": id_cat}), 201

@app.route('/api/categorias/<int:id_cat>', methods=['DELETE'])
def api_manejar_categoria(id_cat):
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    eliminar_categoria(id_cat)
    return jsonify({"mensaje": "Categoría eliminada"}), 200

@app.route('/api/productos', methods=['GET'])
def api_lista_productos():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    conn = get_db_connection()
    prods = conn.execute("""
        SELECT p.id_producto, p.nombre, p.id_categoria, c.nombre AS categoria, p.temporada_demanda 
        FROM Producto p 
        LEFT JOIN Categoria c ON p.id_categoria = c.id_categoria
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in prods])

@app.route('/api/productos', methods=['POST'])
def api_crear_producto():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    datos = request.get_json()
    if not datos or not datos.get('nombre') or not datos.get('id_categoria'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    temporada_demanda = datos.get('temporada_demanda', 'Todo el año')
    id_prod = crear_producto(datos['nombre'], datos['id_categoria'], temporada_demanda)
    return jsonify({"mensaje": "Producto creado", "id_producto": id_prod}), 201

@app.route('/api/productos/<int:id_prod>', methods=['DELETE'])
def api_eliminar_producto(id_prod):
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    eliminar_producto(id_prod)
    return jsonify({"mensaje": "Producto eliminado"}), 200

@app.route('/api/lotes', methods=['POST'])
def api_crear_lote():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    datos = request.get_json()
    if not datos or not datos.get('id_producto') or not datos.get('cantidad') or not datos.get('fecha_ingreso'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    id_lote = crear_lote(datos['id_producto'], datos['cantidad'], datos['fecha_ingreso'])
    return jsonify({"mensaje": "Lote registrado", "id_lote": id_lote}), 201

@app.route('/api/salidas', methods=['POST'])
def api_registrar_salida():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    datos = request.get_json()
    if not datos or not datos.get('id_producto') or not datos.get('cantidad'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    despachado = registrar_salida(datos['id_producto'], datos['cantidad'])
    if despachado == 0:
        return jsonify({"error": "No hay stock disponible o vigente"}), 400
    return jsonify({"mensaje": f"Se despacharon {despachado} unidades"}), 200

@app.route('/api/fundaciones', methods=['GET', 'POST'])
def api_fundaciones():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            d = request.get_json()
            if not d or not d.get('nombre'):
                return jsonify({"error": "El nombre es obligatorio"}), 400
            conn.execute("INSERT INTO Fundacion (nombre, contacto_whatsapp, tipo_destino, descripcion) VALUES (?, ?, ?, ?)", (d.get('nombre', ''), d.get('contacto_whatsapp', ''), d.get('tipo_destino', 'Beneficencia'), d.get('descripcion', '')))
            conn.commit()
            return jsonify({"mensaje": "Destino guardado con éxito"}), 201
        
        funden = conn.execute("SELECT * FROM Fundacion ORDER BY id_fundacion DESC").fetchall()
        return jsonify([dict(row) for row in funden]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/fundaciones/<int:id_fundacion>', methods=['PUT', 'DELETE'])
def api_manejar_fundacion(id_fundacion):
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    conn = get_db_connection()
    try:
        if request.method == 'DELETE':
            conn.execute("DELETE FROM Fundacion WHERE id_fundacion = ?", (id_fundacion,))
            conn.commit()
            return jsonify({"mensaje": "Aliado eliminado"}), 200
        elif request.method == 'PUT':
            d = request.get_json()
            conn.execute("UPDATE Fundacion SET nombre = ?, tipo_destino = ?, contacto_whatsapp = ?, descripcion = ? WHERE id_fundacion = ?", (d.get('nombre', ''), d.get('tipo_destino', 'Beneficencia'), d.get('contacto_whatsapp', ''), d.get('descripcion', ''), id_fundacion))
            conn.commit()
            return jsonify({"mensaje": "Aliado actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/forzar_semaforo', methods=['POST'])
def api_forzar_semaforo():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    actualizar_semaforo()
    return jsonify({"mensaje": "Semáforo actualizado"}), 200

@app.route('/api/temporada', methods=['GET'])
def api_temporada():
    if not verificar_autenticacion(): return jsonify({"error": "No autorizado"}), 401
    import datetime
    mes = datetime.date.today().month
    if mes in [4, 5, 6]:
        return jsonify({"temporada": "Calor / Primavera ☀️", "id_temp": "Calor", "alerta": "Alta", "mensaje": "Temperatura est. 32°C. Si el umbral de la fruta es superado, perderá vida útil rápidamente."})
    elif mes in [7, 8, 9]:
        return jsonify({"temporada": "Lluvias / Humedad 🌧️", "id_temp": "Lluvias", "alerta": "Media", "mensaje": "Temperatura est. 27°C. La humedad reduce 15% la vida de las frutas sensibles."})
    elif mes in [12, 1, 2]:
        return jsonify({"temporada": "Invierno / Frío ❄️", "id_temp": "Frío", "alerta": "Baja", "mensaje": "Temperatura est. 18°C. Excelentes condiciones de conservación."})
    else:
        return jsonify({"temporada": "Clima Templado 🍃", "id_temp": "Todo el año", "alerta": "Baja", "mensaje": "Temperatura est. 24°C. Condiciones estándar del almacén."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)