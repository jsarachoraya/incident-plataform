from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from flask import jsonify, send_file
from flask import Flask, render_template, request, redirect, url_for, Response, flash
import csv
from io import StringIO, BytesIO
from flask import Response, session 
from datetime import datetime
from models.incidencia import (
    create_table, get_all_incidencias, get_incidencia_by_id, create_incidencia, update_incidencia, delete_incidencia,
    search_incidencias, filter_incidencias, create_comentarios_table, get_comentarios_by_incidencia_id,
    create_comentario, get_alerta_vencimiento, count_comentarios_by_incidencia_id, create_prorrogas_table,
    create_prorroga, get_prorrogas_by_incidencia_id, get_connection, filter_incidencias_activas,
    filter_incidencias_historicas, crate_usuarios_table, seed_admin,
)

app = Flask (__name__)

app.secret_key = "super_secret_key"

create_table()

create_comentarios_table()

create_prorrogas_table()

crate_usuarios_table()

seed_admin()

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
#################################### DESPLEGABLE RESUMEN OPERATIVO ######################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/")
def index():

    if "usuario" not in session:
        return redirect(url_for("login"))
    
    search_text = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()
    alerta = request.args.get("alerta", "").strip()

    page = int(request.args.get("page", 1))
    per_page = 50

    incidencias = filter_incidencias_activas(search_text, estado, prioridad)



    incidencias_con_alerta = []

    for inc in incidencias:
        inc_dict = dict(inc)
        inc_dict["alerta_vencimiento"] = get_alerta_vencimiento(inc_dict)
        incidencias_con_alerta.append(inc_dict)

    vencidas = 0
    por_vencer = 0
    en_tiempo = 0
    cliente = 0
    interno = 0

    for inc in incidencias_con_alerta:
        if inc["alerta_vencimiento"] == "vencida":
            vencidas += 1
        elif inc["alerta_vencimiento"] == "por_vencer":
            por_vencer += 1
        elif inc["alerta_vencimiento"] == "en_tiempo":
            en_tiempo += 1

        if inc["origen"] == "cliente":
            cliente += 1
        elif inc["origen"] == "interno":
            interno += 1

    if alerta:
        incidencias_con_alerta = [
            inc for inc in incidencias_con_alerta
            if inc["alerta_vencimiento"] == alerta
        ]

    total = len(incidencias_con_alerta)
    total_pages = (total + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    incidencias_paginadas = incidencias_con_alerta[start:end]

    criticas = sum(1 for i in incidencias if i["prioridad"] == "alta")
    abiertas = sum(1 for i in incidencias if i["estado"] == "abierta")

    return render_template(
        "index.html",
        incidencias=incidencias_paginadas,
        vencidas=vencidas,
        por_vencer=por_vencer,
        en_tiempo=en_tiempo,
        cliente=cliente,
        interno=interno,
        search_text=search_text,
        estado_actual=estado,
        prioridad_actual=prioridad,
        alerta_actual=alerta,
        page=page,
        total_pages=total_pages,
        total_incidencias=len(incidencias),
        criticas=criticas,
        abiertas=abiertas,
    )


@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("login"))
    
    incidencias = filter_incidencias_activas("", "", "")

    incidencias_con_alerta = []

    for inc in incidencias:
        inc_dict = dict(inc)
        inc_dict["alerta_vencimiento"] = get_alerta_vencimiento(inc_dict)
        incidencias_con_alerta.append(inc_dict)

    vencidas = 0
    por_vencer = 0
    en_tiempo = 0
    cliente = 0
    interno = 0
    criticas = 0
    abiertas = 0

    for inc in incidencias_con_alerta:
        if inc["alerta_vencimiento"] == "vencida":
            vencidas += 1
        elif inc["alerta_vencimiento"] == "por_vencer":
            por_vencer += 1
        elif inc["alerta_vencimiento"] == "en_tiempo":
            en_tiempo += 1

        if inc["origen"] == "cliente":
            cliente += 1
        elif inc["origen"] == "interno":
            interno += 1

        if inc["prioridad"] == "critica":
            criticas += 1
        
        if inc["estado"]  == "abierta":
            abiertas += 1

    total_incidencias = len(incidencias_con_alerta)
    
    return render_template(
        "dashboard.html",
        vencidas=vencidas,
        por_vencer=por_vencer,
        en_tiempo=en_tiempo,
        cliente=cliente,
        interno=interno,
        criticas=criticas,
        abiertas=abiertas,
        total_incidencias=total_incidencias  
    )

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
########################################## LOGIN/LOGOUT #################################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM usuarios
            WHERE username = %s AND password = %s
        """, (username, password))

        usuario = cursor.fetchone()

        conn.close()

        if usuario:
            session["usuario"] = usuario["username"]
            session["rol"] = usuario["rol"]

            return redirect(url_for("index"))
        
        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos."
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
################################# HISORICO DE INCIDENCIAS GESTIONADAS ###################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/historico")
def historico():

    search_text = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()

    page = int(request.args.get("page", 1))
    per_page = 50

    incidencias = filter_incidencias_historicas(search_text, estado, prioridad)

    print("HISTORICO", incidencias)

    if incidencias:
        print("TIPO PRIMERA:", type(incidencias[0]))
        print("PRIMERA:", incidencias[0])

    incidencias_con_alerta = []

    for inc in incidencias:
        inc_dict = dict(inc)
        inc_dict["alerta_vencimiento"] = get_alerta_vencimiento(inc_dict)
        incidencias_con_alerta.append(inc_dict)

    total = len(incidencias_con_alerta)
    total_pages = (total + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page

    incidencias_paginadas = incidencias_con_alerta[start:end]

    return render_template(
        "historico.html",
        incidencias=incidencias_paginadas,
        search_text=search_text,
        estado_actual=estado,
        prioridad_actual=prioridad,
        page=page,
        total_pages=total_pages
    )



#///////////////////////////////////////////////////////////////////////////////////////////////////////////#
###################################### DESPLEGABLE FILTROS ESTADOS ##########################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/api/grafico_estado")
def api_grafico_estado():
    search_text = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()
    alerta = request.args.get("alerta", "").strip()

    incidencias = filter_incidencias(search_text, estado, prioridad)

    estado_abierta = 0
    estado_progreso = 0
    estado_resuelta = 0
    estado_cerrada = 0

    for inc in incidencias:
        inc_dict = dict(inc)
        inc_dict["alerta_vencimiento"] = get_alerta_vencimiento(inc)

        if alerta and inc_dict["alerta_vencimiento"] != alerta:
            continue

        if inc["estado"] == "abierta":
            estado_abierta += 1
        elif inc["estado"] == "en progreso":
            estado_progreso += 1
        elif inc["estado"] == "resuelta":
            estado_resuelta += 1
        elif inc["estado"] == "cerrada":
            estado_cerrada += 1

    return jsonify({
        "labels": ["Abierta", "En progreso", "Resuelta", "Cerrada"],
        "data": [
            estado_abierta,
            estado_progreso,
            estado_resuelta,
            estado_cerrada
        ]
    })

@app.route("/api/grafico_origen")
def api_grafico_origen():
    search_text = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()

    incidencias = filter_incidencias_activas(search_text, estado, prioridad)

    cliente = 0
    interno = 0

    for inc in incidencias:
        if inc["origen"] == "cliente":
            cliente += 1
        elif inc["origen"] == "interno":
            interno += 1

    return jsonify({
        "labels": ["Cliente", "Interno"],
        "data": [cliente, interno]
    })

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////#
########################################## BOTON PARA EXPORTAR A EXCEL ##########################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/exportar_excel")
def exportar_excel():
    search_text = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()
    alerta = request.args.get("alerta", "").strip()

    incidencias = filter_incidencias(search_text, estado, prioridad)

    wb = Workbook()
    ws = wb.active
    ws.title = "Incidencias"

    headers = [
        "ID", "Título", "Descripción", "Estado", "Prioridad",
        "Origen", "Identificación", "Tiempo estimado",
        "Fecha límite", "Alerta", "Fecha cración", "Fecha actualización"
    ]

    ws.append(headers)

    for inc in incidencias:
        inc_dict = dict(inc)
        inc_dict["alerta_vencimiento"] = get_alerta_vencimiento(inc)

        if alerta and inc_dict["alerta_vencimiento"] != alerta:
            continue

        identificacion = (
            inc_dict["nombre_cliente"]
            if inc_dict["origen"] == "cliente"
            else inc_dict["legajo"]
        )

        ws.append([
            inc_dict["id"],
            inc_dict["titulo"],
            inc_dict["descripcion"],
            inc_dict["estado"],
            inc_dict["prioridad"],
            inc_dict["origen"],
            identificacion,
            inc_dict["tiempo_estimado"],
            inc_dict["fecha_limite"],
            inc_dict["alerta_vencimiento"].replace("_", " "),
            inc_dict["fecha_creacion"],
            inc_dict["fecha_actualizacion"],
        ])

    header_fill = PatternFill("solid", fgColor="D9EAF7")

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for column_cells in ws.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter

        for cell in column_cells:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        ws.column_dimensions[column_letter].width = min(max_length +2, 40)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="incidencias_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
####################################### DETALLE DE INCIDENCIA ###########################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/incidencia/<int:incidencia_id>")
def detalle_incidencia(incidencia_id):
    incidencia = get_incidencia_by_id(incidencia_id)
    prorrogas = get_prorrogas_by_incidencia_id(incidencia_id)

    if not incidencia:
        return "Incidencia no encontrada", 404
    
    comentarios = get_comentarios_by_incidencia_id(incidencia_id)
    historial = get_comentarios_by_incidencia_id(incidencia_id)

    incidencia_dict = dict(incidencia)
    incidencia_dict["alerta_vencimiento"] = get_alerta_vencimiento(incidencia_dict)
    sugerencias = generar_sugerencia(
        incidencia_dict,
        comentarios=comentarios,
        prorrogas=prorrogas
    )

    mostrar_ia = False
    
    if incidencia_dict["alerta_vencimiento"] == "vencida" and incidencia_dict["prioridad"] == "critica":
        mostrar_ia = True

    if prorrogas and len(prorrogas) > 1:
        mostrar_ia = True

    return render_template(
        "incidencia_detalle.html",
        incidencia=incidencia_dict,
        comentarios=comentarios,
        historial=historial,
        prorrogas=prorrogas,
        sugerencias=sugerencias,
        mostrar_ia=mostrar_ia
    )

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
############################### ASISTENTE DE RESOLUCION (SUGERENCIAS AUTOMATICAS) ####################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

#PARA INCORPORAR IA
def get_alerta_vencimiento(inc):
    if not inc["fecha_limite"]:
        return None
        
    fecha_limite = datetime.fromisoformat(inc["fecha_limite"])
    ahora = datetime.now()

    if fecha_limite < ahora:
        return "vencida" \
        "" \
        ""
    elif (fecha_limite - ahora).days <= 1:
        return "por_vencer" 
    else:
        return "en_tiempo"

def generar_sugerencia(inc, comentarios=None, prorrogas=None):
    sugerencias = []

    titulo = (inc["titulo"] or "").lower()
    descripcion = (inc["descripcion"] or "").lower()
    texto = titulo + " " + descripcion

    #LOGIN

    if "login" in texto or "acceso" in  texto:
        sugerencias.append("Vereficar credenciales del usuario y estado de la sesión.")
        sugerencias.append("Revisar logs de autenticación.")

    #BASE DE DATOS

    if "base" in texto or "db" in texto or "sql" in texto:
        sugerencias.append("Validar conexión a base de datos.")
        sugerencias.append("Revisar consultas SQL recientes.")

    #RED

    if "red" in texto or "conexion" in texto:
        sugerencias.append("Verificar conectividad y estado de red.")
        sugerencias.append("Revisar firewall o accesos.")

    #PRIORIDAD

    if inc["prioridad"] == "critica":
        sugerencias.append("Incidencia crítica: asignar recurso inmediato.")

    #ALERTA

    alerta = inc.get("alerta_vencimiento")
    if alerta == "vencida":
        sugerencias.append("La incidencia está vencida: evaluar escalamiento inmediato o solicitar prórroga justificada.")
    
    if prorrogas is not None and len(prorrogas) > 1:
        sugerencias.append("¡Múltiples! prórrogas detectadas: evaluar asistencia IA para resolución.")

    elif alerta == "por_vencer":
        sugerencias.append("La incidencia está próxima a vencer: priorizar resolución.")

    #ORIGEN

    if inc["origen"] == "cliente":
        sugerencias.append("Incidencia de cliente: mantener comunicacion activa y documentar avances.")

    elif inc["origen"] == "interno":
        sugerencias.append("Incidencia interna: validar legajo y área responsable.")

    #COMENTARIOS

    if comentarios is not None:
        if len(comentarios) == 0:
            sugerencias.append("No hay comentarios: agregar diagnóstico antes de avanzar.")
        elif len(comentarios) > 5:
            sugerencias.append("Demasiados comentarios: revisar historial para evitar reporcesos.")

    #PRORROGAS

    if prorrogas is not None:
        if len(prorrogas) > 0:
            sugerencias.append("La incidencia tiene prórrogas: evaluar cusa raíz de la demora.")

    
        #IA EN CASOS EXTREMOS
    if alerta == "vencida" and inc["prioridad"] == "critica":
        sugerencias.append("¡CASO CRÍTICO VENCIDO!: SE RECOMIENDA ANÁLISIS AVANZADO (IA).")

    #DEFAULT

    if not sugerencias:
        sugerencias.append("Revisar logs generales del sistema.")
        sugerencias.append("Validar cambios recientes en la aplicación.")

    return sugerencias

#////////////////////////////////////////////////////////////////////////////////////////////////////////////#
################################### AGREGAR COMENTARIOS A LA INCIDENCIA ######################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/incidencia/<int:incidencia_id>/comentario", methods=["POST"])
def agregar_comentario(incidencia_id):
    incidencia = get_incidencia_by_id(incidencia_id)

    if not incidencia:
        return "Incidencia no encontrada", 404
    
    contenido = request.form["contenido"].strip()

    if contenido:
        create_comentario(incidencia_id, contenido)

    return redirect(url_for("detalle_incidencia", incidencia_id=incidencia_id))
    

@app.route("/crear", methods=["GET", "POST"])
def crear():

    if "usuario" not in session:
        return redirect(url_for("login"))
    
    if session["rol"] not in ["admin", "operador"]:
        flash("No tiene permiso para realizar esta accion", "warning")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        prioridad = request.form["prioridad"]
        origen = request.form["origen"]
        nombre_cliente = request.form.get("nombre_cliente", "").strip()
        legajo = request.form.get("legajo", "").strip()
        tiempo_estimado = request.form["tiempo_estimado"]
        fecha_limite = request.form["fecha_limite"]
        
        if origen == "cliente" and not nombre_cliente:
            error = "Si el origen es cliente, debe ingresar el nombre del cliente."
            return render_template("incidencia_form.html", incidencia=None, error=error)
    
        if origen == "interno" and not legajo:
            error = "Si el origen es interno, debe ingresar el legajo."
            return render_template("incidencia_form.html", incidencia=None, error=error)

        create_incidencia(
            titulo,
            descripcion,
            prioridad,
            origen,
            nombre_cliente,
            legajo,
            tiempo_estimado,
            fecha_limite
        )
        flash("Incidencia creada correctamente", "success")
        return redirect(url_for("index"))
    
    return render_template("incidencia_form.html", incidencia=None, error=None)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////#
######################################### EDITAR INCIDENCIA ###############################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/editar/<int:incidencia_id>", methods=["GET", "POST"])
def editar(incidencia_id):
    incidencia = get_incidencia_by_id(incidencia_id)

    if not incidencia:
        return "Incidencia no encontrada", 404
    
    if incidencia["estado"] == "cerrada":
        return "No se puede editar una incidencia cerrada."
    
    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        estado = request.form["estado"]
        prioridad = request.form["prioridad"]
        origen = request.form["origen"]
        nombre_cliente = request.form.get("nombre_cliente", "").strip()
        legajo = request.form.get("legajo", "").strip()
        tiempo_estimado = request.form["tiempo_estimado"]
        fecha_limite = incidencia["fecha_limite"]

        incidencia_actual = dict(incidencia)
        alerta_vencimiento = get_alerta_vencimiento(incidencia_actual)
        total_comentarios = count_comentarios_by_incidencia_id(incidencia_id)

        if estado in ["resuelta", "cerrada"] and alerta_vencimiento == "vencida" and total_comentarios == 0:
            error = "No se puede cerrar o resolver una incidencia vencida sin agregar al menos un comentario."
            return render_template(
                "incidencia_form.html",
                incidencia=incidencia,
                error=error
            )
        
        if origen == "cliente" and not nombre_cliente:
            error = "Si el origen es cliente, debe ingresar el nombre del cliente."
            return render_template(
                "incidencia_form.html",
                incidencia=incidencia,
                error=error
            )
        
        if origen == "interno" and not legajo:
            error = "Si el origen es interno, debe ingresar el legajo."
            return render_template(
                "incidencia_form.html",
                incidencia=incidencia,
                error=error
            )
        
        update_incidencia(
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
        )
        flash("Incidencia actualizada", "info")
        return redirect(url_for("index"))
    
    return render_template("incidencia_form.html", incidencia=incidencia, error=None)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
###################################### SOLICITAR PRORROGA ########################################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/incidencia/<int:incidencia_id>/prorroga", methods=["POST"])
def solicitar_prorroga(incidencia_id):
    incidencia = get_incidencia_by_id(incidencia_id)

    if not incidencia:
        return "Incidencia no encontrada/", 404
    
    nueva_fecha_limite = request.form["nueva_fecha_limite"].strip()
    motivo = request.form["motivo"].strip()

    if not nueva_fecha_limite or not motivo:
        return "La nueva fecha límite y el motivo son obligatorios."
    
    create_prorroga(
        incidencia_id,
        incidencia["fecha_limite"] or "",
        nueva_fecha_limite,
        motivo
    )

    return redirect(url_for("detalle_incidencia", incidencia_id=incidencia_id))

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////#
###################################### APROBAR O RECHAZAR PRORROGA SOLICITADA ####################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/prorroga/<int:prorroga_id>/aprobar")
def aprobar_prorroga(prorroga_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener prórroga
    cursor.execute("SELECT * FROM prorrogas WHERE id = %s", (prorroga_id,))
    prorroga = cursor.fetchone()

    if not prorroga:
        return "Prórroga no encontrada", 404
    
    # Actualizar estado
    cursor.execute("""
        UPDATE prorrogas
        SET estado = 'aprobada'
        WHERE id = %s
    """, (prorroga_id,))

    # Actualizar decha limite en incidencia
    cursor.execute("""
        UPDATE incidencias
        SET fecha_limite = %s
        WHERE id = %s
    """, (prorroga["nueva_fecha_limite"], prorroga["incidencia_id"]))

    conn.commit()
    conn.close()

    return redirect(url_for("detalle_incidencia", incidencia_id=prorroga["incidencia_id"]))

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
####################################### RECHAZAR PRORROGA SOLICITADA ####################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/prorroga/<int:prorroga_id>/rechazar")
def rechazar_prorroga(prorroga_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE prorrogas
        SET estado = 'rechazada'
        WHERE id = %s
    """, (prorroga_id,))

    conn.commit()
    conn.close()

    return redirect(request.referrer)

#///////////////////////////////////////////////////////////////////////////////////////////////////////#
######################################## ELIMINAR INCIDENCIA ############################################
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

@app.route("/eliminar/<int:incidencia_id>")
def eliminar(incidencia_id):

    if "usuario" not in session:
        return redirect(url_for("login"))
    
    if session["rol"] not in ["admin", "operador"]:
        flash("No tiene permiso para realizar esta accion", "warning")
        return redirect(url_for("index"))
    
    delete_incidencia(incidencia_id)
    flash("Incidencia eliminada", "danger")
    return redirect(url_for("index"))

if __name__== "__main__":
    app.run(debug=True)