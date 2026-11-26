"""TaskManager: sistema web para la gestión de tareas de TechSolutions.

Backend en Flask con base de datos SQLite. Expone una API REST en /api/tareas
que consume la interfaz web (templates/index.html + static/js/app.js).
"""

import os
import sqlite3

from flask import Flask, current_app, g, jsonify, render_template, request

VERSION = "1.0.0"
ESTADOS = ("Pendiente", "En proceso", "Terminada")
PRIORIDADES = ("Alta", "Media", "Baja")
MAX_NOMBRE = 120
MAX_DESCRIPCION = 1000

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
        descripcion = datos.get("descripcion", "").strip()
        if len(descripcion) > MAX_DESCRIPCION:
            errores.append(f"La descripción no puede superar {MAX_DESCRIPCION} caracteres.")
        else:
            limpio["descripcion"] = descripcion

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

    init_db(app.config["DATABASE"])
    app.teardown_appcontext(cerrar_db)

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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
