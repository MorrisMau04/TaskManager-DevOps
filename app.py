"""TaskManager: sistema web para la gestión de tareas de TechSolutions.

Backend en Flask con base de datos SQLite. Expone una API REST en /api/tareas
que consume la interfaz web (templates/index.html + static/js/app.js).
"""

import logging
import os
import sqlite3
import time

from flask import Flask, current_app, g, jsonify, render_template, request

VERSION = "1.0.0"
ESTADOS = ("Pendiente", "En proceso", "Terminada")
PRIORIDADES = ("Alta", "Media", "Baja")
MAX_NOMBRE = 120
MAX_DESCRIPCION = 1000
UMBRAL_LENTO_MS = 500

ESQUEMA = """
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    prioridad TEXT NOT NULL DEFAULT 'Media',
    estado TEXT NOT NULL DEFAULT 'Pendiente',
    creada_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    actualizada_en TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


# ---------------------------------------------------------------------------
# Acceso a datos
# ---------------------------------------------------------------------------
def conectar(ruta):
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    return conexion


def get_db():
    """Devuelve la conexión a SQLite de la petición actual."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def cerrar_db(_error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db(ruta):
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with conectar(ruta) as conexion:
        conexion.executescript(ESQUEMA)


def obtener_tarea(tarea_id):
    fila = get_db().execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    return dict(fila) if fila else None


def actualizar_tarea(tarea_id, campos):
    """Actualiza solo las columnas validadas (las claves vienen de validar_tarea)."""
    asignaciones = ", ".join(f"{columna} = ?" for columna in campos)
    db = get_db()
    db.execute(
        f"UPDATE tareas SET {asignaciones}, actualizada_en = datetime('now', 'localtime') "
        "WHERE id = ?",
        (*campos.values(), tarea_id),
    )
    db.commit()


def error(mensaje, codigo, detalles=None):
    return jsonify({"error": mensaje, "detalles": detalles or []}), codigo


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------
def normalizar(valor, permitidos):
    """Acepta el valor sin importar mayúsculas y devuelve la forma oficial."""
    if not isinstance(valor, str):
        return None
    for opcion in permitidos:
        if valor.strip().lower() == opcion.lower():
            return opcion
    return None


def validar_tarea(datos, parcial=False):
    """Valida los datos de una tarea.

    Devuelve (campos_limpios, errores). Con parcial=True solo se validan los
    campos enviados (se usa al editar).
    """
    if not isinstance(datos, dict):
        return {}, ["El cuerpo de la petición debe ser un objeto JSON."]

    limpio, errores = {}, []

    if "nombre" in datos or not parcial:
        nombre = datos.get("nombre")
        nombre = nombre.strip() if isinstance(nombre, str) else ""
        if not nombre:
            errores.append("El nombre de la tarea es obligatorio.")
        elif len(nombre) > MAX_NOMBRE:
            errores.append(f"El nombre no puede superar {MAX_NOMBRE} caracteres.")
        else:
            limpio["nombre"] = nombre

    if "descripcion" in datos or not parcial:
        # La descripción es opcional: null o ausente se guarda como texto vacío.
        descripcion = datos.get("descripcion")
        if descripcion is None:
            descripcion = ""
        if not isinstance(descripcion, str):
            errores.append("La descripción debe ser texto.")
        elif len(descripcion.strip()) > MAX_DESCRIPCION:
            errores.append(f"La descripción no puede superar {MAX_DESCRIPCION} caracteres.")
        else:
            limpio["descripcion"] = descripcion.strip()

    if "prioridad" in datos or not parcial:
        prioridad = normalizar(datos.get("prioridad", "Media"), PRIORIDADES)
        if prioridad is None:
            errores.append(f"La prioridad debe ser una de: {', '.join(PRIORIDADES)}.")
        else:
            limpio["prioridad"] = prioridad

    if "estado" in datos or not parcial:
        estado = normalizar(datos.get("estado", "Pendiente"), ESTADOS)
        if estado is None:
            errores.append(f"El estado debe ser uno de: {', '.join(ESTADOS)}.")
        else:
            limpio["estado"] = estado

    return limpio, errores


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------
def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "taskmanager.db")
        ),
        JSON_AS_ASCII=False,
    )
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app.config["INICIO"] = time.time()

    init_db(app.config["DATABASE"])
    app.teardown_appcontext(cerrar_db)

    # ---------------------------- Monitoreo ----------------------------
    @app.before_request
    def iniciar_cronometro():
        g.inicio = time.perf_counter()

    @app.after_request
    def registrar_peticion(respuesta):
        inicio = g.pop("inicio", None)
        if inicio is not None:
            duracion_ms = (time.perf_counter() - inicio) * 1000
            respuesta.headers["X-Response-Time"] = f"{duracion_ms:.1f}ms"
            nivel = logging.WARNING if duracion_ms > UMBRAL_LENTO_MS else logging.INFO
            app.logger.log(
                nivel, "%s %s -> %s (%.1f ms)",
                request.method, request.path, respuesta.status_code, duracion_ms,
            )
        return respuesta

    @app.get("/health")
    def health():
        """Punto de verificación para el monitoreo y la plataforma de despliegue."""
        inicio = time.perf_counter()
        try:
            total = get_db().execute("SELECT COUNT(*) FROM tareas").fetchone()[0]
            estado_bd = "ok"
        except sqlite3.Error:
            app.logger.exception("La base de datos no responde")
            total, estado_bd = None, "error"
        cuerpo = {
            "status": "ok" if estado_bd == "ok" else "degradado",
            "base_de_datos": estado_bd,
            "tareas_registradas": total,
            "version": VERSION,
            "uptime_segundos": round(time.time() - app.config["INICIO"]),
            "tiempo_bd_ms": round((time.perf_counter() - inicio) * 1000, 2),
        }
        return jsonify(cuerpo), 200 if estado_bd == "ok" else 503

    @app.errorhandler(500)
    def error_interno(exc):
        app.logger.error("Error interno en %s %s: %s", request.method, request.path,
                         getattr(exc, "original_exception", exc))
        if request.path.startswith("/api/"):
            return error("Ocurrió un error inesperado en el servidor.", 500)
        return "Error interno del servidor", 500

    @app.errorhandler(404)
    def no_encontrado(_exc):
        if request.path.startswith("/api/"):
            return error("Recurso no encontrado.", 404)
        return "Página no encontrada", 404

    # ---------------------------- Interfaz -----------------------------
    @app.get("/")
    def index():
        return render_template(
            "index.html", version=VERSION, estados=ESTADOS, prioridades=PRIORIDADES
        )

    # ------------------------ RF02: Consultar ---------------------------
    @app.get("/api/tareas")
    def listar_tareas():
        consulta = "SELECT * FROM tareas"
        filtros, parametros = [], []
        for campo, permitidos in (("estado", ESTADOS), ("prioridad", PRIORIDADES)):
            valor = request.args.get(campo)
            if valor:
                normalizado = normalizar(valor, permitidos)
                if normalizado is None:
                    return error(f"Filtro de {campo} inválido.", 400,
                                 [f"Valores permitidos: {', '.join(permitidos)}."])
                filtros.append(f"{campo} = ?")
                parametros.append(normalizado)
        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)
        consulta += (
            " ORDER BY CASE prioridad WHEN 'Alta' THEN 1 WHEN 'Media' THEN 2 ELSE 3 END,"
            " id DESC"
        )
        filas = get_db().execute(consulta, parametros).fetchall()
        return jsonify([dict(fila) for fila in filas])

    @app.get("/api/tareas/<int:tarea_id>")
    def consultar_tarea(tarea_id):
        tarea = obtener_tarea(tarea_id)
        if tarea is None:
            return error("La tarea no existe.", 404)
        return jsonify(tarea)

    # ------------------------ RF01: Registrar ---------------------------
    @app.post("/api/tareas")
    def registrar_tarea():
        campos, errores = validar_tarea(request.get_json(silent=True))
        if errores:
            return error("Los datos de la tarea no son válidos.", 400, errores)
        db = get_db()
        cursor = db.execute(
            "INSERT INTO tareas (nombre, descripcion, prioridad, estado) VALUES (?, ?, ?, ?)",
            (campos["nombre"], campos["descripcion"], campos["prioridad"], campos["estado"]),
        )
        db.commit()
        return jsonify({
            "mensaje": "Tarea registrada correctamente.",
            "tarea": obtener_tarea(cursor.lastrowid),
        }), 201

    # ------------------------- RF03: Editar -----------------------------
    @app.put("/api/tareas/<int:tarea_id>")
    def editar_tarea(tarea_id):
        if obtener_tarea(tarea_id) is None:
            return error("La tarea no existe.", 404)
        campos, errores = validar_tarea(request.get_json(silent=True), parcial=True)
        if errores:
            return error("Los datos de la tarea no son válidos.", 400, errores)
        if not campos:
            return error("No se envió ningún campo para actualizar.", 400)
        actualizar_tarea(tarea_id, campos)
        return jsonify({
            "mensaje": "Tarea actualizada correctamente.",
            "tarea": obtener_tarea(tarea_id),
        })

    # ------------------------- RF04: Eliminar ---------------------------
    @app.delete("/api/tareas/<int:tarea_id>")
    def eliminar_tarea(tarea_id):
        if obtener_tarea(tarea_id) is None:
            return error("La tarea no existe.", 404)
        db = get_db()
        db.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
        db.commit()
        return jsonify({"mensaje": "Tarea eliminada correctamente.", "id": tarea_id})

    # --------------------- RF05: Cambiar estado -------------------------
    @app.patch("/api/tareas/<int:tarea_id>/estado")
    def cambiar_estado(tarea_id):
        if obtener_tarea(tarea_id) is None:
            return error("La tarea no existe.", 404)
        datos = request.get_json(silent=True) or {}
        estado = normalizar(datos.get("estado"), ESTADOS)
        if estado is None:
            return error("Estado inválido.", 400,
                         [f"Valores permitidos: {', '.join(ESTADOS)}."])
        actualizar_tarea(tarea_id, {"estado": estado})
        return jsonify({
            "mensaje": f"Estado cambiado a «{estado}».",
            "tarea": obtener_tarea(tarea_id),
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
