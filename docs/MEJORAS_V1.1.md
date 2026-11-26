# Propuestas de mejora: TaskManager v1.1.0

| # | Mejora | Motivo | Prioridad | Estimación |
|---|--------|--------|-----------|------------|
| 1 | Base de datos persistente (PostgreSQL administrado) | SQLite se pierde al reiniciar el servicio en Render. | Crítica | 6 h |
| 2 | Autenticación de usuarios y asignación de responsables | Cada empleado debe ver y atender sus propias tareas. | Alta | 10 h |
| 3 | Búsqueda por texto y fecha límite por tarea | Facilitar encontrar tareas e identificar vencimientos. | Media | 5 h |
| 4 | Notificaciones de tareas próximas a vencer | Evitar retrasos en actividades críticas. | Media | 6 h |
| 5 | Reporte de productividad (tareas terminadas por semana) | Seguimiento para la dirección de TechSolutions. | Baja | 4 h |

## Planeación de la versión 1.1.0
1. Registrar cada mejora como Issue en la columna **Backlog** del tablero, fase **Plan**.
2. Priorizar en reunión del equipo y mover a **To Do** las mejoras 1 y 2.
3. Desarrollar cada una en su rama `feature/*` con Pull Request y revisión.
4. Mantener la Integración Continua en verde y agregar pruebas para cada mejora.
5. Publicar el Release `v1.1.0` y repetir las pruebas funcionales y el monitoreo.
