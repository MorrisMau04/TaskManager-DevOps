# Notas de versión

## v1.0.0: Primera versión estable de TaskManager

### Funcionalidades
- **RF01 Registrar tareas:** nombre obligatorio, descripción opcional, prioridad y estado; mensaje de confirmación.
- **RF02 Consultar tareas:** listado ordenado por prioridad y resumen por estado.
- **RF03 Editar tareas:** edición desde el mismo formulario, con opción para cancelar.
- **RF04 Eliminar tareas:** con confirmación previa.
- **RF05 Cambiar estado:** Pendiente, En proceso y Terminada, directamente desde el listado.
- **RF06 Asignar prioridad:** Alta, Media o Baja, con colores y filtros.

### Calidad y automatización
- 34 pruebas unitarias con pytest.
- Integración Continua en cada push y Pull Request a `main`.
- Entrega Continua: paquete descargable generado al publicar un Release.
- Despliegue Continuo en Render cuando la Integración Continua termina con éxito.
- Monitoreo programado de disponibilidad y tiempo de respuesta (`/health`).

### Correcciones
- Error 500 al guardar una tarea sin descripción.
- Configuración de pytest (`pytest.ini`) para que la Integración Continua encuentre `app.py`.
