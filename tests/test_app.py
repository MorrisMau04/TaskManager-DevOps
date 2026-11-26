"""Pruebas unitarias de TaskManager (pytest)."""
import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    """Aplicación con una base de datos SQLite temporal para cada prueba."""
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "pruebas.db")})


@pytest.fixture
def client(app):
    return app.test_client()


def crear(client, **datos):
    datos.setdefault("nombre", "Realizar actividad DevOps")
    return client.post("/api/tareas", json=datos)


def test_registro_tarea():
    """Ejemplo del documento: estructura básica de una tarea."""
    tarea = {"nombre": "Realizar actividad DevOps", "estado": "Pendiente"}
    assert tarea["nombre"] == "Realizar actividad DevOps"
    assert tarea["estado"] == "Pendiente"


def test_pagina_principal_carga(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "TaskManager" in respuesta.get_data(as_text=True)


# ----------------------------- RF02: Consultar -----------------------------
def test_listado_vacio(client):
    respuesta = client.get("/api/tareas")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_consultar_tarea_inexistente(client):
    respuesta = client.get("/api/tareas/999")
    assert respuesta.status_code == 404
    assert respuesta.get_json()["error"] == "La tarea no existe."


# ----------------------------- RF01: Registrar -----------------------------
def test_registrar_tarea(client):
    respuesta = crear(client, descripcion="Configurar el pipeline", prioridad="Alta")
    assert respuesta.status_code == 201
    cuerpo = respuesta.get_json()
    assert cuerpo["mensaje"] == "Tarea registrada correctamente."
    tarea = cuerpo["tarea"]
    assert tarea["nombre"] == "Realizar actividad DevOps"
    assert tarea["descripcion"] == "Configurar el pipeline"
    assert tarea["prioridad"] == "Alta"
    assert tarea["estado"] == "Pendiente"


def test_registrar_tarea_sin_nombre_muestra_validacion(client):
    respuesta = client.post("/api/tareas", json={"nombre": "   ", "descripcion": "x"})
    assert respuesta.status_code == 400
    assert "El nombre de la tarea es obligatorio." in respuesta.get_json()["detalles"]


def test_tarea_registrada_aparece_en_listado(client):
    crear(client, nombre="Elaborar documentación")
    nombres = [t["nombre"] for t in client.get("/api/tareas").get_json()]
    assert "Elaborar documentación" in nombres


# ------------------------------ RF03: Editar -------------------------------
def test_editar_tarea(client):
    tarea_id = crear(client).get_json()["tarea"]["id"]
    respuesta = client.put(f"/api/tareas/{tarea_id}",
                           json={"nombre": "Nombre corregido", "descripcion": "Nueva"})
    assert respuesta.status_code == 200
    tarea = client.get(f"/api/tareas/{tarea_id}").get_json()
    assert tarea["nombre"] == "Nombre corregido"
    assert tarea["descripcion"] == "Nueva"


def test_editar_tarea_inexistente(client):
    assert client.put("/api/tareas/999", json={"nombre": "X"}).status_code == 404


def test_editar_tarea_con_nombre_vacio(client):
    tarea_id = crear(client).get_json()["tarea"]["id"]
    respuesta = client.put(f"/api/tareas/{tarea_id}", json={"nombre": ""})
    assert respuesta.status_code == 400


# ------------------------------ RF04: Eliminar -----------------------------
def test_eliminar_tarea(client):
    tarea_id = crear(client).get_json()["tarea"]["id"]
    respuesta = client.delete(f"/api/tareas/{tarea_id}")
    assert respuesta.status_code == 200
    assert client.get(f"/api/tareas/{tarea_id}").status_code == 404
    assert client.get("/api/tareas").get_json() == []


def test_eliminar_tarea_inexistente(client):
    assert client.delete("/api/tareas/999").status_code == 404


# ------------------------ RF05 y RF06: Estado y prioridad ------------------
@pytest.mark.parametrize("estado", ["Pendiente", "En proceso", "Terminada"])
def test_cambiar_estado(client, estado):
    tarea_id = crear(client).get_json()["tarea"]["id"]
    respuesta = client.patch(f"/api/tareas/{tarea_id}/estado", json={"estado": estado})
    assert respuesta.status_code == 200
    listado = client.get("/api/tareas").get_json()
    assert listado[0]["estado"] == estado


def test_cambiar_estado_invalido(client):
    tarea_id = crear(client).get_json()["tarea"]["id"]
    respuesta = client.patch(f"/api/tareas/{tarea_id}/estado", json={"estado": "Archivada"})
    assert respuesta.status_code == 400


@pytest.mark.parametrize("prioridad", ["Alta", "Media", "Baja"])
def test_prioridad_se_guarda(client, prioridad):
    tarea = crear(client, prioridad=prioridad).get_json()["tarea"]
    assert tarea["prioridad"] == prioridad


def test_prioridad_invalida(client):
    assert crear(client, prioridad="Urgentísima").status_code == 400


def test_filtrar_por_estado_y_prioridad(client):
    crear(client, nombre="A", prioridad="Alta")
    crear(client, nombre="B", prioridad="Baja", estado="Terminada")
    altas = client.get("/api/tareas?prioridad=Alta").get_json()
    terminadas = client.get("/api/tareas?estado=Terminada").get_json()
    assert [t["nombre"] for t in altas] == ["A"]
    assert [t["nombre"] for t in terminadas] == ["B"]


