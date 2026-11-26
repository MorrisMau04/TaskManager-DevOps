# Matriz de casos de prueba: TaskManager v1.0.0

Pruebas funcionales ejecutadas en el navegador (Chrome, 1280×800 y 390×844) contra la
aplicación servida con `gunicorn app:app` y una base de datos SQLite nueva.
Fecha de ejecución: 25 de noviembre de 2026.

| ID | Prueba | Resultado esperado | Resultado obtenido | Estado |
|----|--------|--------------------|--------------------|--------|
| CP01 | Registrar una tarea | La tarea se guarda correctamente. | Mensaje «Tarea registrada correctamente.» y la tarea aparece en el listado. | Aprobada |
| CP02 | Registrar una tarea sin nombre | El sistema muestra una validación. | La interfaz muestra «El nombre de la tarea es obligatorio.» y la API responde 400. | Aprobada |
| CP03 | Consultar tareas | Se muestra el listado. | Tras recargar se muestran las 3 tareas ordenadas por prioridad (Alta, Media, Baja). | Aprobada |
| CP04 | Editar una tarea | Se actualiza la información. | El nombre y la descripción se actualizaron en el listado. | Aprobada |
| CP05 | Eliminar una tarea | La tarea desaparece del listado. | Se confirmó la eliminación y la tarea ya no aparece después de recargar. | Aprobada |
| CP06 | Cambiar estado | Se actualiza el estado. | Después de recargar, las tareas conservan «En proceso» y «Terminada»; el resumen muestra 1/1/1. | Aprobada |
| CP07 | Seleccionar prioridad | Se guarda la prioridad elegida. | La tarea creada como Baja muestra «Prioridad baja»; el filtro Alta solo muestra la tarea de prioridad alta. | Aprobada |
| CP08 | Registrar una tarea sin descripción | La tarea se guarda con descripción vacía. | Antes de la corrección: «Error 500». Después de la corrección: se guarda correctamente. | Aprobada (tras corrección) |

## Ejemplo de ejecución: CP01 Registrar una tarea
1. Abrir el sistema.
2. En el formulario «Nueva tarea», escribir el nombre: *Elaborar documentación*.
3. Agregar la descripción: *Redactar el manual de usuario del sistema*.
4. Seleccionar prioridad **Alta**.
5. Presionar **Guardar tarea**.
6. Verificar que aparezca el mensaje de confirmación y la tarea en el listado.

## Error encontrado
Durante las pruebas se detectó que al guardar una tarea **sin descripción** el servidor
respondía `500` (`AttributeError: 'NoneType' object has no attribute 'strip'`), porque la
interfaz envía `descripcion: null` cuando el campo está vacío. Se registró como Issue con la
etiqueta `bug`, se agregó una prueba unitaria que lo reproduce (la Integración Continua falló)
y se corrigió en la rama `fix/tarea-sin-descripcion`, con lo que la Integración Continua volvió a pasar.

## Pruebas unitarias automatizadas
`pytest` ejecuta 34 pruebas (tests/test_app.py) en cada push y Pull Request mediante
GitHub Actions: registro, validaciones, consulta, edición, eliminación, estados,
prioridades, filtros, regresión del error anterior y monitoreo (`/health`).
