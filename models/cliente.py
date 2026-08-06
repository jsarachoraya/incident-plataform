from .incidencia import get_connection
from psycopg2.extras import RealDictCursor

def obtener_clientes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM clientes
        WHERE visible_en_clientes = TRUE
        ORDER BY id DESC
    """)

    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    return clientes

def crear_cliente(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO clientes (
            dni,
            nombre,
            apellido,
            empresa,
            email,
            domicilio,
            telefono,
            empresa_telefonica,
            sector,
            estado_cliente,
            estado_riesgo,
            motivo_riesgo,
            puede_reingresar,
            prioridad_cliente,
            notas
        )
        VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
                   
    """, (

        data["dni"],
        data["nombre"],
        data["apellido"],
        data["empresa"],
        data["email"],
        data["domicilio"],
        data["telefono"],
        data["empresa_telefonica"],
        data["sector"],
        data["estado_cliente"],
        data["estado_riesgo"],
        data["motivo_riesgo"],
        data["puede_reingresar"],
        data["prioridad_cliente"],
        data["notas"]

    ))

    conn.commit()

    cursor.close()
    conn.close()

def buscar_cliente_por_dni(dni):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM clientes
        WHERE dni = %s
    """, (dni,))

    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    return cliente

def obtener_cliente_por_id(cliente_id):

    conn = get_connection()
    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute("""
        SELECT *
        FROM clientes
        WHERE id = %s
    """, (cliente_id,))

    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    return cliente


def buscar_cliente_general(valor):

    conn = get_connection()
    cursor = conn.cursor()

    valor_busqueda = f"%{valor}%"

    cursor.execute("""
        SELECT *
        FROM clientes
        WHERE dni ILIKE %s
           OR email ILIKE %s
           OR telefono ILIKE %s
           OR nombre ILIKE %s
           OR apellido ILIKE %s
           OR CONCAT(nombre, ' ', apellido) ILIKE %s
        LIMIT 1
    """, (
        valor_busqueda,
        valor_busqueda,
        valor_busqueda,
        valor_busqueda,
        valor_busqueda,
        valor_busqueda
    ))

    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    return cliente
    
