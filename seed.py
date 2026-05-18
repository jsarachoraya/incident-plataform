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

conn.commit()
conn.close()


