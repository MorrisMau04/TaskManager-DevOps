# Operación y monitoreo

## Qué se monitorea
| Aspecto | Cómo se verifica |
|---------|------------------|
| Disponibilidad | Workflow **Monitoreo** (cada 3 horas) consulta `/health`, `/` y `/api/tareas`; además Render usa `/health` como *health check*. |
| Tiempo de respuesta | Cada respuesta incluye la cabecera `X-Response-Time`; el workflow registra el tiempo total de cada ruta. Las peticiones de más de 500 ms se registran como `WARNING` en los logs. |
| Errores | Los errores 500 se registran en los logs con la ruta afectada; la API responde un JSON controlado. |
| Almacenamiento | `/health` ejecuta una consulta a SQLite y reporta `base_de_datos` y `tareas_registradas`. |
| Funcionalidades | El workflow de despliegue verifica `/health` después de cada despliegue; las pruebas funcionales CP01-CP08 se repiten en la URL pública. |

Si el monitoreo detecta una respuesta distinta de 200, **crea automáticamente un Issue** con la
etiqueta `incidencia`, con fecha de detección, funcionalidad afectada y enlace a la evidencia.

## Mediciones en entorno local (gunicorn, 25/11/2026)
50 peticiones por ruta:

| Ruta | Código | Promedio | p95 | Máximo |
|------|--------|----------|-----|--------|
| `/health` | 200 | 0.8 ms | 0.8 ms | 7.6 ms |
| `/` | 200 | 0.7 ms | 0.9 ms | 7.5 ms |
| `/api/tareas` | 200 | 0.9 ms | 1.1 ms | 7.1 ms |

20 registros de tareas (POST): promedio 2.1 ms. Sin errores 500 en el log.

## Registro de monitoreo en producción
Completar con los resultados del workflow **Monitoreo** (pestaña Actions → Monitoreo → Summary).

| Fecha y hora | `/health` | Tiempo `/health` | `/api/tareas` | Observaciones |
|--------------|-----------|------------------|---------------|---------------|
| | | | | |

## Riesgos conocidos de la plataforma
- En el plan gratuito de Render el sistema de archivos es efímero: la base SQLite se reinicia en
  cada despliegue o reinicio del servicio. Para conservar datos se planea migrar a PostgreSQL (v1.1).
- El servicio gratuito se suspende tras un periodo sin tráfico; la primera petición posterior
  puede tardar varios segundos (arranque en frío).
