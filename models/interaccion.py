from .incidencia import get_connection

def crear_interaccion(cliente_id, tipo_interaccion, descripcion, resultado, usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interacciones_cliente (
            cliente_id,
            tipo_interaccion,
            descripcion,
            resultado,
            usuario
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        cliente_id,
        tipo_interaccion,
        descripcion,
        resultado,
        usuario
    ))

    conn.commit()
    cursor.close()
    conn.close()


def obtener_interacciones_por_cliente(cliente_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * 
        FROM interacciones_cliente
        WHERE cliente_id = %s
        ORDER BY fecha DESC
    """, (cliente_id,))

    interacciones = cursor.fetchall()

    cursor.close()
    conn.close()

    return interacciones


def registrar_evento_automatico(cliente_id, descripcion, usuario):

    crear_interaccion(
        cliente_id=cliente_id,
        tipo_interaccion="evento_sistema",
        descripcion=descripcion,
        resultado="registrado",
        usuario=usuario
    )
    

def obtener_clientes_atendidos_hoy():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT cliente_id) 
        FROM interacciones_cliente
        WHERE DAT(fecha) = CURRENT_DATE
    """)

    cantidad = cursor.fetchall()[0]

    cursor.close()
    conn.close()

    return cantidad

