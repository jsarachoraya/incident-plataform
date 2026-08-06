from .incidencia import get_connection
from psycopg2.extras import RealDictCursor


def crear_oportunidad(cliente_id, producto, monto_estimado, descripcion, usuario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pipeline_oportunidades (
            cliente_id,
            producto,
            monto_estimado,
            descripcion,
            usuario,
            etapa
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        cliente_id,
        producto,
        monto_estimado,
        descripcion,
        usuario,
        "prospecto"
    ))

    conn.commit()
    cursor.close()
    conn.close()


def obtener_oportunidades():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT 
            o.*,
            c.nombre,
            c.apellido,
            c.dni
        FROM pipeline_oportunidades o
        JOIN clientes c ON c.id = o.cliente_id
        ORDER BY o.fecha_creacion DESC
    """)

    oportunidades = cursor.fetchall()

    cursor.close()
    conn.close()

    return oportunidades


def obtener_oportunidades_por_etapa(etapa):

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT 
            o.*,
            c.nombre,
            c.apellido,
            c.dni
        FROM pipeline_oportunidades o
        JOIN clientes c ON c.id = o.cliente_id
        WHERE o.etapa = %s
        ORDER BY o.fecha_creacion DESC
    """, (etapa,))

    oportunidades = cursor.fetchall()

    cursor.close()
    conn.close()

    return oportunidades


def actualizar_etapa_oportunidad(oportunidad_id, nueva_etapa):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pipeline_oportunidades
        SET etapa = %s
        WHERE id = %s
    """, (
        nueva_etapa,
        oportunidad_id
    )) 
    conn.commit()
    cursor.close()
    conn.close()
