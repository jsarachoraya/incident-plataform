import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timedelta
  

load_dotenv()

DB_NAME = "database.db"

def get_connection():
        
    db_type = os.getenv("DB_TYPE", "sqlite")

    if db_type == "postgres":

        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        
        return conn

    conn = sqlite3.connect(DB_NAME)

    conn.row_factory = sqlite3.Row

    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidencias (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT NOT NULL DEFAULT 'abierta',
            prioridad TEXT NOT NULL DEFAULT 'media',
            origen TEXT NOT NULL,
            nombre_cliente TEXT,
            legajo TEXT,
            tiempo_estimado TEXT,
            fecha_limite TEXT,
            fecha_creacion TEXT NOT NULL,
            fecha_actualizacion TEXT NOT NULL
         )
    """)

    conn.commit()
    conn.close()

def get_all_incidencias():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM incidencias ORDER BY id DESC")
    incidencias = cursor.fetchall()

    conn.close()
    return incidencias

def filter_incidencias(search_text, estado, prioridad):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM incidencias WHERE 1=1"
    params = []

    if search_text:
        query += " AND (titulo ILIKE %s OR descripcion ILIKE %s)"
        params.extend([f"%{search_text}%", f"%{search_text}%"])

    if estado:
        query += " AND estado = %s"
        params.append(estado)

    if prioridad:
        query += " AND prioridad = %s"
        params.append(prioridad)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    resultados = cursor.fetchall()

    conn.close()
    return resultados
    
def get_incidencia_by_id(incidencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM incidencias WHERE id = %s", (incidencia_id,))
    incidencia = cursor.fetchone()

    conn.close()
    return incidencia
    
def create_incidencia(
    titulo,
    descripcion,
    prioridad,
    origen,
    nombre_cliente,
    legajo,
    tiempo_estimado,
    fecha_limite
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(""" 
        INSERT INTO incidencias (
            titulo,
            descripcion,
            estado,
            prioridad,
            origen,
            nombre_cliente,
            legajo,
            tiempo_estimado,
            fecha_limite,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (%s, %s, 'abierta', %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        titulo,
        descripcion,
        prioridad,
        origen,
        nombre_cliente,
        legajo,
        tiempo_estimado,
        fecha_limite,
        now,
        now
    ))
        
    conn.commit()
    conn.close()

def update_incidencia(
    incidencia_id,
    titulo,
    descripcion,
    estado,
    prioridad,
    origen,
    nombre_cliente,
    legajo,
    tiempo_estimado,
    fecha_limite
):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE incidencias
        SET titulo = %s,
            descripcion = %s,
            estado = %s,
            prioridad = %s,
            origen = %s,
            nombre_cliente = %s,
            legajo = %s,
            tiempo_estimado = %s,
            fecha_limite = %s,
            fecha_actualizacion = %s
        WHERE id = %s
    """, (
        titulo,
        descripcion,
        estado,
        prioridad,
        origen,
        nombre_cliente,
        legajo,
        tiempo_estimado,
        fecha_limite,
        now,
        incidencia_id
    ))

    conn.commit()
    conn.close()

def delete_incidencia(incidencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM incidencias WHERE id = %s", (incidencia_id,))

    conn.commit()
    conn.close()

def search_incidencias(search_text):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"%{search_text}"

    cursor.execute("""
        SELECT * FROM incidencias
        WHERE titulo ILIKE %s OR descripcion ILIKE %s
        ORDER BY id DESC
    """, (query, query))

    incidencias = cursor.fetchall()

    conn.close()
    return incidencias

def filter_incidencias (search_text="", estado="", prioridad=""):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM incidencias WHERE 1=1"
    params = []

    if search_text:
        sql += " AND (titulo ILIKE %s OR descripcion ILIKE %s)"
        query = f"%{search_text}%"    
        params.extend([query, query])

    if estado:
        sql += " AND estado = %s"
        params.append(estado)

    if prioridad:
        sql += " AND prioridad = %s"
        params.append(prioridad)

    sql += " ORDER BY id DESC"

    cursor.execute(sql, params)
    incidencias = cursor.fetchall()

    conn.close()
    return incidencias


def filter_incidencias_activas(search_text, estado, prioridad):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM incidencias
        WHERE estado NOT IN ('resuelta', 'cerrada')
    """
    params = []

    if search_text:
        query += " AND (titulo ILIKE %s OR descripcion ILIKE %s)"
        params.extend([f"%{search_text}%", f"%{search_text}%"])

    if estado:
        query += " AND estado = %s"
        params.append(estado)

    if prioridad:
        query += " AND prioridad = %s"
        params.append(prioridad)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    conn.close()

    return resultados


def filter_incidencias_historicas(search_text, estado, prioridad):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM incidencias
        WHERE estado IN ('resuelta', 'cerrada')
    """
    params = []

    if search_text:
        query += " AND (titulo ILIKE %s OR descripcion ILIKE %s)"
        params.extend([f"%{search_text}%", f"%{search_text}%"])

    if estado:
        query += " AND estado = %s"
        params.append(estado)

    if prioridad:
        query += " AND prioridad = %s"
        params.append(prioridad)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    conn.close()
    return resultados



def create_comentarios_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comentarios (
            id SERIAL PRIMARY KEY,
            incidencia_id INTEGER NOT NULL,
            contenido TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            FOREIGN KEY (incidencia_id) REFERENCES incidencias (id)
        )        
    """)

    conn.commit()
    conn.close()


def get_comentarios_by_incidencia_id(incidencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM comentarios
        WHERE incidencia_id = %s
        ORDER BY ID DESC
    """, (incidencia_id,))

    comentarios = cursor.fetchall()

    conn.close()
    return comentarios

def create_comentario(incidencia_id, contenido):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO comentarios (
            incidencia_id,
            contenido,
            fecha_creacion
        )
        VALUES (%s, %s, %s)
    """, (incidencia_id, contenido, now))

    conn.commit()
    conn.close()


def get_alerta_vencimiento(incidencia):
    fecha_limite = incidencia["fecha_limite"]
    estado = incidencia["estado"]

    if not fecha_limite:
        return "sin fecha"    
    
    if estado in ["resuelta", "cerrada"]:
        return "cerrada"
    
    try:
        fecha_limite_dt = datetime.strptime(fecha_limite, "%Y-%m-%dT%H:%M")
    except ValueError:
        try:
            fecha_limite_dt = datetime.strptime(fecha_limite, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "formato invalido"
        
    ahora = datetime.now()

    if ahora > fecha_limite_dt:
        return "vencida"
        
    if fecha_limite_dt - ahora <= timedelta(hours=24):
        return "por_vencer"
        
    return "en_tiempo"


def count_comentarios_by_incidencia_id(incidencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as total
        FROM comentarios
        WHERE incidencia_id = %s
    """, (incidencia_id,))

    result = cursor.fetchone()

    conn.close()
    return result["total"]

def create_prorrogas_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prorrogas (
            id SERIAL PRIMARY KEY,
            incidencia_id INTEGER NOT NULL,
            fecha_limite_anterior TEXT NOT NULL,
            nueva_fecha_limite TEXT NOT NULL,
            motivo TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            fecha_solicitud TEXT NOT NULL,
            FOREIGN KEY (incidencia_id) REFERENCES incidencias (id)
        )
    """)

    conn.commit()
    conn.close()


def create_prorroga(incidencia_id, fecha_limite_anterior, nueva_fecha_limite, motivo):
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO prorrogas (
            incidencia_id,
            fecha_limite_anterior,
            nueva_fecha_limite,
            motivo,
            fecha_solicitud
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (incidencia_id, fecha_limite_anterior, nueva_fecha_limite, motivo, now))

    conn.commit()
    conn.close()


def get_prorrogas_by_incidencia_id(incidencia_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM prorrogas
        WHERE incidencia_id = %s
        ORDER BY id DESC
    """, (incidencia_id,))

    prorrogas = cursor.fetchall()

    conn.close()
    return prorrogas



def crate_usuarios_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
            
        )
    """)

    conn.commit()
    conn.close()


def seed_admin():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE username = %s",
        ("admin",)

    )
    
    usuario = cursor.fetchone()
    

    if not usuario:
        cursor.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (%s, %s, %s)
        """, ("admin", "admin123", "admin"))

    conn.commit()
    conn.close()