import random
from datetime import datetime, timedelta
from models.incidencia import get_connection

titulos = ["Error login", "Sistema caído", "Bug reporte", "Problema red", "Acceso bloqueado"]
prioridades = ["alta", "media", "baja"]
origenes = ["cliente", "interno"]

clientes = ["Juan Perez", "Cosme Fulanito", "Maria Lopez"]
legajos = ["A123", "B456", "C789"]

conn = get_connection()
cursor = conn.cursor()

#INSERTAR DATOS DE PRUEBA Y CARGAR SEED EN CONSOLA#
for i in range(100):
    titulo = random.choice(titulos)
    descrpcion = "Descripcion de prueba"
    prioridad = random.choice(prioridades)
    origen = random.choice(origenes)

    nombre_cliente = random.choice(clientes) if origen == "cliente" else ""
    legajo = random.choice(legajos) if origen == "interno" else ""

    tiempo_estimado = f"{random.randint(1,5)} dias"

    fecha_limite = datetime.now() + timedelta(days=random.randint(-5, 10))
    fecha_limite_str = fecha_limite.strftime("%Y-%m-%dT%H:%M")
    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_actualizacion = fecha_creacion

    cursor.execute("""
        INSERT INTO incidencias (
            titulo, descripcion, estado, prioridad,
            origen, nombre_cliente, legajo,
            tiempo_estimado, fecha_limite,
            fecha_creacion,
            fecha_actualizacion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        titulo,
        descrpcion,
        "abierta",
        prioridad,
        origen,
        nombre_cliente,
        legajo,
        tiempo_estimado,
        fecha_limite_str,
        fecha_creacion,
        fecha_actualizacion
    ))


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        dni VARCHAR(20) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100),
        empresa VARCHAR(100),
        email VARCHAR(120),
        telefono VARCHAR(50),
        sector VARCHAR(100),
        estado_cliente VARCHAR(50) DEFAULT 'prospecto',
        estado_riesgo VARCHAR(20) DEFAULT 'sin_evaluar',
        motivo_riesgo TEXT,
        puede_reingresar BOOLEAN DEFAULT TRUE,
        prioridad_cliente VARCHAR(20) DEFAULT 'media',
        notas TEXT,
        fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interacciones_cliente (
        id SERIAL PRIMARY KEY,
        cliente_id INTEGER NOT NULL,
        tipo_interaccion VARCHAR(50),
        descripcion TEXT,
        resultado VARCHAR(100),
        usuario VARCHAR(100),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
    )
                   
    """)
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_oportunidades (
        id SERIAL PRIMARY KEY,
        cliente_id INTEGER NOT NULL,
        producto VARCHAR(100) NOT NULL,
        etapa VARCHAR(50) DEFAULT 'prospecto',
        monto_estimado NUMERIC(12,2) DEFAULT 0,
        probabilidad INTEGER DEFAULT 10,
        descripcion TEXT,
        usuario VARCHAR(100),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
                   
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos_cliente (
        id SERIAL PRIMARY KER,
        cliente_id INTEGER NOT NULL,
        producto VARCHAR(100) NOT NULL,
        estado_producto VARCHAR(50) DEFAULT 'actvo',
        monto NUMERIC(12,2) DEFAULT 0,
        fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        observaciones TEXT,
                   
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
                   
    )

    """)

conn.commit()
conn.close()


