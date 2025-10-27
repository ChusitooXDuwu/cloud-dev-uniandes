
# Pruebas de Carga — Entrega 3 (Escenario Realista)

---
## Objetivo General

Evaluar la **capacidad y estabilidad** del API bajo condiciones de carga realistas, simulando 300 usuarios concurrentes distribuidos entre flujos de autenticación, carga de videos y consultas de detalle.  
El objetivo principal fue identificar:

- el **punto de saturación** del backend,
    
- la **capacidad sostenida de throughput**, y
    
- la **degradación progresiva del tiempo de respuesta (p95)** en cargas mixtas.
    

---

## Configuración de la Prueba

|Parámetro|Valor|
|---|---|
|**Tipo de prueba**|Stress + Soak (mixta)|
|**Usuarios concurrentes**|300|
|**Ramp-up**|180 s|
|**Duración estable (hold)**|600 s|
|**Pasos de carga**|100 → 200 → 300 → 400 usuarios|
|**Throughput objetivo**|0–50 → 100 → 150 → 200 req/s|
|**Archivo multimedia**|`flex_mini.mp4` (6.5 MB)|
|**Tiempos de espera (think time)**|200–800 ms (Uniform Random Timer)|
|**Login**|Once Only Controller (JWT reutilizado)|
|**Correlación dinámica**|JSON Extractor: `video_id`|
|**Validaciones**|Response Assertion (201 OK), JSON Assertion (`task_id`), JSR223 success code|
|**Gestión de red**|Keep-Alive activo, DNS TTL bajo, Cache Manager y Cookie Manager habilitados|
|**Métricas monitorizadas**|Latencia, Throughput, CPU, RAM, errores, tráfico de red|

---

## Escenarios Probados

### Escenario 1 — Autenticación + Upload (multipart)

**Objetivo:** Medir la estabilidad del endpoint de subida bajo alta concurrencia con archivos medianos (~6 MB).

|Métrica|Resultado|
|---|---|
|**Requests totales**|3,600|
|**HTTP 2xx/201**|3,516 (97.7%)|
|**Errores 4xx/5xx**|84 (2.3%) — principalmente 502 Gateway Timeout|
|**Tiempo promedio (ms)**|2,380|
|**p95 (ms)**|4,310|
|**p99 (ms)**|5,890|
|**Throughput (req/s)**|6.0|
|**Ancho de banda enviado**|~210 Mbps|
|**Uso CPU API**|82% pico|
|**RAM usada (EC2)**|5.6 GB máx|

**Análisis:**  
Durante los primeros 5 minutos, el API mantuvo estabilidad.  
El punto de degradación comenzó tras los 250 usuarios concurrentes, donde p95 superó los 4 s y se presentaron respuestas 502 por saturación momentánea de ancho de banda.  
El código 201 se devolvió correctamente en 100% de los casos válidos.

**Conclusión:**  
La capacidad máxima sostenible para operaciones de _upload_ con archivos medianos se estima en **220 usuarios concurrentes**, con margen de CPU disponible y sin errores críticos.

---

### Escenario 2 — Listado y Detalle (consultas GET)

**Objetivo:** Analizar rendimiento del API para lecturas intensivas y acceso a detalles.

|Métrica|Resultado|
|---|---|
|**Requests totales**|9,000|
|**HTTP 2xx**|100%|
|**Errores**|0|
|**Tiempo promedio (ms)**|670|
|**p95 (ms)**|1,210|
|**p99 (ms)**|1,980|
|**Throughput (req/s)**|18.2|
|**Ancho de banda recibido**|~85 Mbps|
|**CPU promedio**|64%|
|**RAM usada**|3.2 GB|

**Análisis:**  
Las operaciones de lectura son mucho más ligeras, y el API pudo sostener más de 18 req/s sin degradación perceptible.  
No se evidenciaron errores HTTP ni caídas de conexión.

**Conclusión:**  
El sistema soporta **300–400 usuarios concurrentes en consultas puras** sin sobrecarga visible. Ideal para dashboards o streaming de datos ligeros.

---

### Escenario 3 — Mixto (60% lecturas, 40% cargas)

**Objetivo:** Evaluar comportamiento global del sistema ante carga representativa del uso real.

|Métrica|Resultado|
|---|---|
|**Requests totales**|12,600|
|**Tasa de éxito**|98.4%|
|**Errores (4xx/5xx)**|1.6%|
|**Tiempo promedio (ms)**|1,430|
|**p95 (ms)**|2,980|
|**Throughput (req/s)**|12.4|
|**CPU promedio**|78%|
|**RAM usada**|5.0 GB|
|**Latencia media red**|75 ms|
|**Ancho de banda combinado**|~270 Mbps|

**Análisis:**  
La combinación de lectura y escritura es donde se alcanza la carga más realista.  
El throughput se estabiliza en 12–13 req/s con p95 < 3 s.  
Los pocos errores observados (principalmente 502) se produjeron durante la fase de ramp-up.

**Conclusión:**  
El sistema muestra **resiliencia y estabilidad general** en escenarios mixtos.  
El **punto de saturación general** se ubica entre **320–350 usuarios concurrentes** o **~13 req/s sostenidos**.

---

## Conclusiones Generales

**Fortalezas**

- Arquitectura estable bajo carga mixta (lecturas + uploads).
    
- Manejo correcto de JWT y multipart bajo alta concurrencia.
    
- Latencias estables en p95 ≤ 3 s.
    
- Mecanismo de retry reduce fallas transitorias.
    
- No se observaron memory leaks ni fugas en heap.
    

**Debilidades detectadas**

- Saturación del ancho de banda en subidas >250 usuarios.
    
- Ligeros 502/504 por límite de threads de servidor FastAPI (Gunicorn/Uvicorn).
    
- Falta de balanceo horizontal (1 instancia EC2 única).
    
- No hay cacheo de lecturas; todo pasa directo a base de datos.
    

---

##  Recomendaciones

|Área|Mejora sugerida|
|---|---|
|**Infraestructura**|Escalar a 2 instancias EC2 con Traefik o ALB (Round Robin).|
|**FastAPI**|Habilitar `--workers 4 --threads 2` en Gunicorn para mejorar paralelismo I/O.|
|**Uploads**|Desacoplar con colas (SQS/Azure Queue) + worker asíncrono (Celery o Dramatiq).|
|**Lecturas**|Añadir Redis o Memcached para `GET /api/videos` frecuentes.|
|**Storage**|Migrar subidas a S3/Azure Blob con pre-signed URLs.|
|**Observabilidad**|Integrar Prometheus + Grafana con métricas de p95, CPU, RAM, red, I/O.|
|**Stress Continuo**|Automatizar el plan JMeter con GitHub Actions (runner EC2 temporal).|

---

## Capacidad estimada (resumen final)

|Tipo de carga|Usuarios sostenibles|Throughput estable|p95 (ms)|Error %|
|---|---|---|---|---|
|**Upload (multipart)**|220|6.0 req/s|4,310|2.3%|
|**Lecturas (GET)**|400|18.2 req/s|1,210|0%|
|**Mixto (60/40)**|320|12.4 req/s|2,980|1.6%|

---

## Próximos pasos

1. Probar la infraestructura con **autoescalado (ASG)** y balanceador (ALB o Traefik).
    
2. Repetir la prueba con **tamaños de archivo variables** (1 MB, 10 MB, 25 MB).
    
3. Ejecutar una **Soak Test de 1 hora** para validar estabilidad a largo plazo.
    
4. Medir **p99 y desviación estándar** para validar consistencia.
    
5. Documentar métricas con InfluxDB + Grafana para observabilidad continua.
    
