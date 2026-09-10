import sqlite3
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = os.getenv('DB_PATH', 'inventario.db')

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_base_datos():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS Usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Categoria (
                id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                dias_vida_util INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Producto (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                id_categoria INTEGER,
                stock_minimo INTEGER DEFAULT 0,
                FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria) ON DELETE SET NULL
            );
            CREATE TABLE IF NOT EXISTS Lote (
                id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER,
                cantidad_inicial REAL NOT NULL,
                cantidad_actual REAL NOT NULL,
                fecha_ingreso DATE NOT NULL,
                estado_semaforo TEXT DEFAULT 'Verde',
                FOREIGN KEY (id_producto) REFERENCES Producto(id_producto) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS Fundacion (
                id_fundacion INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto_whatsapp TEXT,
                tipo_destino TEXT DEFAULT 'Beneficencia',
                descripcion TEXT
            );
            CREATE TABLE IF NOT EXISTS Movimiento (
                id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lote INTEGER,
                tipo_movimiento TEXT NOT NULL,
                cantidad REAL NOT NULL,
                fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_lote) REFERENCES Lote(id_lote) ON DELETE CASCADE
            );
        """)
        
        # Migración automática si la tabla Fundacion ya existía con el esquema anterior
        cursor.execute("PRAGMA table_info(Fundacion)")
        columnas = [col[1] for col in cursor.fetchall()]
        if 'tipo_destino' not in columnas:
            cursor.execute("ALTER TABLE Fundacion ADD COLUMN tipo_destino TEXT DEFAULT 'Beneficencia'")
        if 'descripcion' not in columnas:
            cursor.execute("ALTER TABLE Fundacion ADD COLUMN descripcion TEXT DEFAULT ''")
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inicializando BD: {e}")
        conn.rollback()
    finally:
        conn.close()

def inicializar_superusuario():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE rol = 'superuser'")
        if cursor.fetchone()[0] == 0:
            pswd_hash = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO Usuario (username, password_hash, rol) VALUES (?, ?, ?)",
                ('admin', pswd_hash, 'superuser')
            )
            conn.commit()
    finally:
        conn.close()

def login(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE username = ?", (username,))
        usuario = cursor.fetchone()
        if usuario and check_password_hash(usuario['password_hash'], password):
            return dict(usuario)
        return None
    finally:
        conn.close()

def actualizar_semaforo():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.id_lote, l.fecha_ingreso, c.dias_vida_util, l.estado_semaforo
            FROM Lote l
            JOIN Producto p ON l.id_producto = p.id_producto
            JOIN Categoria c ON p.id_categoria = c.id_categoria
            WHERE l.cantidad_actual > 0 AND l.estado_semaforo != 'Negro'
        """)
        lotes_activos = cursor.fetchall()
        hoy = datetime.date.today()
        lotes_a_actualizar = []

        for lote in lotes_activos:
            fecha_ingreso = datetime.datetime.strptime(lote['fecha_ingreso'], '%Y-%m-%d').date()
            dias_restantes = lote['dias_vida_util'] - (hoy - fecha_ingreso).days
            
            if dias_restantes <= 0: nuevo_estado = 'Negro'
            elif dias_restantes <= 2: nuevo_estado = 'Rojo'
            elif dias_restantes <= 5: nuevo_estado = 'Amarillo'
            else: nuevo_estado = 'Verde'
                
            if nuevo_estado != lote['estado_semaforo']:
                lotes_a_actualizar.append((nuevo_estado, lote['id_lote']))
        
        if lotes_a_actualizar:
            cursor.executemany("UPDATE Lote SET estado_semaforo = ? WHERE id_lote = ?", lotes_a_actualizar)
            conn.commit()
    finally:
        conn.close()

def crear_categoria(nombre, dias_vida_util):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Categoria (nombre, dias_vida_util) VALUES (?, ?)", (nombre, dias_vida_util))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def actualizar_categoria(id_cat, nombre, dias):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Categoria SET nombre = ?, dias_vida_util = ? WHERE id_categoria = ?", (nombre, dias, id_cat))
        conn.commit()
    finally:
        conn.close()

def eliminar_categoria(id_cat):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Categoria WHERE id_categoria = ?", (id_cat,))
        conn.commit()
    finally:
        conn.close()

def crear_producto(nombre, id_categoria, stock_minimo):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Producto (nombre, id_categoria, stock_minimo) VALUES (?, ?, ?)", (nombre, id_categoria, stock_minimo))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def eliminar_producto(id_prod):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Producto WHERE id_producto = ?", (id_prod,))
        conn.commit()
    finally:
        conn.close()

def crear_lote(id_producto, cantidad, fecha_ingreso):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Lote (id_producto, cantidad_inicial, cantidad_actual, fecha_ingreso) VALUES (?, ?, ?, ?)", (id_producto, cantidad, cantidad, fecha_ingreso))
        id_lote = cursor.lastrowid
        cursor.execute("INSERT INTO Movimiento (id_lote, tipo_movimiento, cantidad) VALUES (?, 'Entrada', ?)", (id_lote, cantidad))
        conn.commit()
        return id_lote
    finally:
        conn.close()

def obtener_inventario():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.id_lote, p.nombre AS producto, c.nombre AS categoria, 
                   l.cantidad_actual, l.fecha_ingreso, l.estado_semaforo
            FROM Lote l
            JOIN Producto p ON l.id_producto = p.id_producto
            JOIN Categoria c ON p.id_categoria = c.id_categoria
            WHERE l.cantidad_actual > 0
            ORDER BY l.fecha_ingreso ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def obtener_resumen_general():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id_producto, p.nombre AS producto, c.nombre AS categoria, 
                   SUM(l.cantidad_actual) AS stock_total
            FROM Lote l
            JOIN Producto p ON l.id_producto = p.id_producto
            JOIN Categoria c ON p.id_categoria = c.id_categoria
            WHERE l.cantidad_actual > 0 AND l.estado_semaforo != 'Negro'
            GROUP BY p.id_producto
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def registrar_salida(id_producto, cantidad_requerida):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_lote, cantidad_actual 
            FROM Lote 
            WHERE id_producto = ? AND cantidad_actual > 0 AND estado_semaforo != 'Negro'
            ORDER BY fecha_ingreso ASC
        """, (id_producto,))
        lotes = cursor.fetchall()
        cantidad_restante = float(cantidad_requerida)
        
        for lote in lotes:
            if cantidad_restante <= 0:
                break
            id_lote = lote['id_lote']
            disponible = lote['cantidad_actual']
            
            if disponible <= cantidad_restante:
                cursor.execute("UPDATE Lote SET cantidad_actual = 0 WHERE id_lote = ?", (id_lote,))
                cursor.execute("INSERT INTO Movimiento (id_lote, tipo_movimiento, cantidad) VALUES (?, 'Salida', ?)", (id_lote, disponible))
                cantidad_restante -= disponible
            else:
                nueva_cantidad = disponible - cantidad_restante
                cursor.execute("UPDATE Lote SET cantidad_actual = ? WHERE id_lote = ?", (nueva_cantidad, id_lote))
                cursor.execute("INSERT INTO Movimiento (id_lote, tipo_movimiento, cantidad) VALUES (?, 'Salida', ?)", (id_lote, cantidad_restante))
                cantidad_restante = 0

        conn.commit()
        return cantidad_requerida - cantidad_restante
    finally:
        conn.close()