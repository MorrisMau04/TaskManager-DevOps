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


