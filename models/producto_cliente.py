from .incidencia import get_connection
from psycopg2.extras import RealDictCursor


def obtener_productos_cliente(cliente_id):

    conn = get_connection()
    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute("""
        SELECT *
        FROM productos_cliente
        WHERE cliente_id = %s
        ORDER BY fecha_alta DESC
    """, (cliente_id,))

    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return productos


def crear_producto_cliente(
    cliente_id,
    producto,
    estado_producto,
    monto,
    observaciones,
    variante=None,
    margen=None
):
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos_cliente(
            cliente_id,
            producto,
            estado_producto,
            monto,
            observaciones,
            variante,
            margen
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)

    """, (
        cliente_id,
        producto,
        estado_producto,
        monto,
        observaciones,
        variante,
        margen
    ))
    
    conn.commit()

    cursor.close()
    conn.close()


def cliente_tiene_producto(cliente_id, producto):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM productos_cliente
        WHERE cliente_id = %s
        AND producto = %s
        AND estado_producto != 'baja'
        LIMIT 1
    """, (cliente_id, producto,))

    existe = cursor.fetchone()

    cursor.close()
    conn.close()

    return existe is not None


def eliminar_producto_cliente(producto_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM productos_cliente
        WHERE id = %s
    """, (producto_id,))

    conn.commit()

    cursor.close()
    conn.close()
