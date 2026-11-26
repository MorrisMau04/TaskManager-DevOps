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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
