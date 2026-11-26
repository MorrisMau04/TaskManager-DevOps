# TaskManager-DevOps

Sistema web para la gestión de tareas de **TechSolutions**, desarrollado aplicando las fases
del ciclo de vida DevOps con GitHub (Projects, Issues, Pull Requests, Actions y Releases).

[![Integracion Continua](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)

## Funcionalidades

| Código | Funcionalidad | Descripción |
|--------|---------------|-------------|
| RF01 | Registrar tareas | Agregar tareas con nombre, descripción, prioridad y estado. |
| RF02 | Consultar tareas | Listado ordenado por prioridad y resumen por estado. |
| RF03 | Editar tareas | Modificar la información de una tarea. |
| RF04 | Eliminar tareas | Eliminar tareas existentes (con confirmación). |
| RF05 | Cambiar estado | Pendiente, En proceso o Terminada. |
| RF06 | Asignar prioridad | Alta, Media o Baja, con filtros. |

## Tecnologías

- **Frontend:** HTML, CSS y JavaScript (sin frameworks).
- **Backend:** Python 3.12 con Flask.
- **Base de datos:** SQLite.
- **Pruebas:** pytest.
- **Automatización:** GitHub Actions.
- **Despliegue:** Render con gunicorn.

## Estructura

```text
TaskManager-DevOps/
├── app.py                  # Aplicación Flask y API REST
├── requirements.txt
├── render.yaml             # Configuración de despliegue en Render
├── templates/index.html    # Interfaz
├── static/css/style.css
├── static/js/app.js
├── tests/test_app.py       # Pruebas unitarias
├── docs/                   # Historias de usuario, matriz de pruebas, monitoreo y mejoras
└── .github/
    ├── workflows/          # ci.yml, entrega.yml, despliegue.yml, monitoreo.yml
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md
```

## Ejecutar en tu computadora

```bash
git clone https://github.com/MorrisMau04/TaskManager-DevOps.git
cd TaskManager-DevOps
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir <http://127.0.0.1:5000>. La base de datos se crea automáticamente en `instance/taskmanager.db`
(se puede cambiar con la variable de entorno `DATABASE_PATH`).

## Pruebas

```bash
pytest -v
```

## API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/tareas?estado=&prioridad=` | Lista las tareas (filtros opcionales). |
| GET | `/api/tareas/<id>` | Consulta una tarea. |
| POST | `/api/tareas` | Registra una tarea. Cuerpo: `{"nombre", "descripcion", "prioridad", "estado"}`. |
| PUT | `/api/tareas/<id>` | Edita los campos enviados. |
| PATCH | `/api/tareas/<id>/estado` | Cambia el estado. Cuerpo: `{"estado": "En proceso"}`. |
| DELETE | `/api/tareas/<id>` | Elimina una tarea. |
| GET | `/health` | Estado de la aplicación y de la base de datos (monitoreo). |

## Flujo DevOps

| Fase | Herramienta | Resultado en este repositorio |
|------|-------------|-------------------------------|
| Plan | GitHub Projects e Issues | Tablero con Backlog, To Do, In Progress, Review y Done; historias de usuario en `docs/`. |
| Code | Git y GitHub | Ramas `feature/*` y `fix/*` integradas mediante Pull Requests. |
| Build / CI | GitHub Actions | `ci.yml` ejecuta pytest en cada push y Pull Request a `main`. |
| Test | pytest y pruebas funcionales | 34 pruebas unitarias y matriz CP01-CP08 (`docs/MATRIZ_DE_PRUEBAS.md`). |
| Release | GitHub Releases y Actions | `v1.0.0`; `entrega.yml` genera el paquete descargable. |
| Deploy | GitHub Actions y Render | `despliegue.yml` despliega cuando la CI pasa en `main`. |
| Operate / Monitor | Issues y Actions | `monitoreo.yml` revisa `/health` cada 3 horas y abre Issues de incidencia. |

## Despliegue en Render

1. En <https://render.com> crear una cuenta y conectar GitHub.
2. **New → Blueprint** y elegir este repositorio (usa `render.yaml`), o **New → Web Service** con:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. En el servicio: **Settings → Deploy Hook**, copiar la URL.
4. En GitHub: **Settings → Secrets and variables → Actions**:
   - Secreto `RENDER_DEPLOY_HOOK_URL` = URL del Deploy Hook.
   - Variable `APP_URL` = URL pública (por ejemplo `https://taskmanager-devops.onrender.com`).

> En el plan gratuito de Render el disco es efímero: las tareas se reinician en cada despliegue.

## Equipo

| Integrante | Rol |
|------------|-----|
| Mauricio Solis Ruiz | Product Owner y desarrollador backend |
| Mauricio Solis Ruiz | Desarrollador de interfaz y documentación |
| Mauricio Solis Ruiz | Ingeniero DevOps / QA |
