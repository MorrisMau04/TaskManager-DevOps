# Historias de usuario: TaskManager

| ID | Requerimiento | Prioridad | Estimación | Responsable |
|----|---------------|-----------|------------|-------------|
| HU-01 | RF01 Registrar tareas | Crítica | 3 h | Integrante 1 |
| HU-02 | RF02 Consultar tareas | Alta | 4 h | Integrante 2 |
| HU-03 | RF03 Editar tareas | Alta | 3 h | Integrante 2 |
| HU-04 | RF04 Eliminar tareas | Alta | 2 h | Integrante 3 |
| HU-05 | RF05 Cambiar estado | Alta | 2 h | Integrante 1 |
| HU-06 | RF06 Asignar prioridad | Media | 1 h | Integrante 1 |

## HU-01: Registrar tareas
**Como** usuario del sistema, **quiero** registrar nuevas tareas **para** organizar mis actividades.

Criterios de aceptación:
- El sistema debe permitir ingresar el nombre de la tarea (obligatorio, máximo 120 caracteres).
- El sistema debe permitir agregar una descripción (opcional).
- El sistema debe permitir seleccionar una prioridad.
- El sistema debe guardar la tarea.
- El sistema debe mostrar un mensaje de confirmación.
- Si el nombre está vacío, el sistema debe mostrar una validación y no guardar.

## HU-02: Consultar tareas
**Como** usuario, **quiero** ver todas las tareas registradas **para** saber qué actividades existen y en qué estado están.

Criterios de aceptación:
- Debe mostrarse el listado con nombre, descripción, prioridad, estado y fecha de actualización.
- Las tareas deben aparecer ordenadas por prioridad (Alta, Media, Baja).
- Debe mostrarse un resumen con el total de tareas pendientes, en proceso y terminadas.
- Si no hay tareas, debe mostrarse el mensaje «No hay tareas para mostrar».

## HU-03: Editar tareas
**Como** usuario, **quiero** modificar la información de una tarea **para** corregir datos o actualizar su alcance.

Criterios de aceptación:
- Debe existir un botón «Editar» en cada tarea que cargue sus datos en el formulario.
- Debe permitir cambiar nombre, descripción, prioridad y estado.
- Debe validar que el nombre no quede vacío.
- Debe permitir cancelar la edición sin guardar cambios.
- Los cambios deben reflejarse en el listado con un mensaje de confirmación.

## HU-04: Eliminar tareas
**Como** usuario, **quiero** eliminar tareas que ya no son necesarias **para** evitar duplicidad de información.

Criterios de aceptación:
- Debe existir un botón «Eliminar» en cada tarea.
- El sistema debe pedir confirmación antes de eliminar.
- La tarea eliminada debe desaparecer del listado y del resumen.
- Debe mostrarse un mensaje de confirmación.

## HU-05: Cambiar estado de tareas
**Como** usuario, **quiero** cambiar el estado de una tarea **para** conocer su progreso.

Criterios de aceptación:
- Debe permitir seleccionar Pendiente.
- Debe permitir seleccionar En proceso.
- Debe permitir seleccionar Terminada.
- El cambio debe reflejarse en el listado de tareas y en el resumen.
- Debe poder filtrarse el listado por estado.

## HU-06: Asignar prioridad
**Como** usuario, **quiero** clasificar las tareas como alta, media o baja **para** atender primero lo más importante.

Criterios de aceptación:
- Debe permitir elegir Alta, Media o Baja al registrar o editar (Media por defecto).
- La prioridad debe mostrarse con un color distinto en cada tarea.
- Debe poder filtrarse el listado por prioridad.
- El sistema debe rechazar valores de prioridad no válidos.
