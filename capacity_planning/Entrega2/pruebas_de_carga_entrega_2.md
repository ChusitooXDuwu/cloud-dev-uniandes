
# 📊 Pruebas de Carga – Entrega 2

**Repositorio:** `capacity-planning/pruebas_de_carga_entrega2.md`  
**Fecha de ejecución:** 26 de octubre de 2025  
**Herramienta utilizada:** Apache JMeter 5.6  
**Entorno:** entorno de despliegue en Coolify (FastAPI + PostgreSQL + Azure Blob Storage)  
**Autenticación:** JWT generado con endpoint `/api/v1/auth/token`  
**Escenarios ejecutados:** Escenario 1 – Carga concurrente de autenticación y carga de archivos; Escenario 2 – Listar y consultar detalles concurrentemente.

---

## 1️⃣ Objetivo

Evaluar la **capacidad de concurrencia** y el **tiempo de respuesta promedio** del API REST implementado, identificando posibles cuellos de botella y validando la estabilidad de la plataforma bajo carga intensiva.  
El enfoque se orienta a determinar cuántos usuarios simultáneos puede soportar el servicio **manteniendo una respuesta estable (≤ 2 s promedio)** y sin errores HTTP 500 o timeout.

---

## 2️⃣ Configuración general de la prueba

|Parámetro|Valor|
|---|---|
|**Herramienta**|Apache JMeter 5.6|
|**Thread Group**|TG Auth + Upload + List + Detail|
|**Número de hilos**|150|
|**Ramp-up**|120 segundos|
|**Duración total**|~ 2 min 30 s|
|**Archivo cargado**|`flex_mini.mp4`|
|**Endpoints probados**|`/auth/token`, `/api/v1/upload`, `/api/v1/list`, `/api/v1/detail/:id`|
|**JWT utilizado**|Token generado durante la sesión de autenticación válida|
|**Persistencia de logs**|`jmeter.log` y `results_scenario.csv`|

Durante la ejecución se observó la creación secuencial de los 150 hilos, completando las operaciones de subida y consulta sin interrupciones críticas. El log confirma la finalización correcta de todos los threads (`Thread finished: TG Auth + Upload + List + Detail 1-150`).

---

## 3️⃣ Escenario 1 – Carga concurrente de autenticación + subida de archivos

**Objetivo:** Validar el comportamiento del sistema al recibir múltiples solicitudes simultáneas de autenticación y carga de archivos de tamaño medio (~5 MB).

### Configuración específica

- 150 usuarios concurrentes autenticándose y subiendo un archivo distinto.
    
- Token JWT reutilizado para minimizar overhead de login.
    
- Validación del código HTTP 200 y tiempos de respuesta.
    

### Resultados obtenidos (promedios extraídos del CSV)

|Métrica|Valor|
|---|---|
|**Samples (reqs)**|150|
|**Éxitos (2xx)**|100 %|
|**Errores (4xx/5xx)**|0 %|
|**Tiempo promedio (ms)**|1 456|
|**P95 (ms)**|2 310|
|**Throughput (req/s)**|7.3|
|**Bytes transmitidos**|≈ 750 MB totales|
|**CPU API**|≈ 65 %|
|**Uso RAM**|≈ 2.1 GB|

### Análisis

- La subida concurrente se mantuvo estable durante la rampa completa.
    
- El pico de uso de CPU se produjo entre los segundos 80 y 120, momento en el que el throughput fue máximo.
    
- No se presentaron timeouts ni errores de autenticación.
    

**Conclusión:** El servicio tolera hasta 150 usuarios simultáneos con tiempos de respuesta aceptables para operaciones de carga media.

---

## 4️⃣ Escenario 2 – Consulta masiva de listado y detalle

**Objetivo:** Analizar la capacidad de respuesta del API REST al consultar masivamente los recursos ya subidos.

### Configuración específica

- 150 hilos ejecutando secuencialmente `GET /api/v1/list` y `GET /api/v1/detail/{id}`.
    
- Autenticación JWT reutilizada.
    
- Tiempo de enfriamiento (think time) = 0.3 s.
    

### Resultados (resumen del CSV)

|Métrica|Valor|
|---|---|
|**Samples (reqs)**|300 (150 list + 150 detail)|
|**Éxitos (2xx)**|100 %|
|**Errores (4xx/5xx)**|0 %|
|**Tiempo promedio (ms)**|812|
|**P95 (ms)**|1 487|
|**Throughput (req/s)**|9.1|
|**CPU API**|≈ 58 %|
|**Uso RAM**|≈ 1.8 GB|

### Análisis

- Las consultas masivas tuvieron mejor rendimiento que las subidas debido al menor peso de los payloads.
    
- Los tiempos de respuesta promedio fueron inferiores a 1 s, demostrando capacidad para carga moderada.
    
- La base de datos no presentó bloqueos ni deadlocks.
    

**Conclusión:** El API es eficiente para lecturas concurrentes masivas y su infraestructura actual puede sostener picos de ≈ 9 solicitudes/segundo.

---

## 5️⃣ Conclusiones generales

- El sistema mostró **estabilidad y ausencia de errores críticos** durante ambos escenarios.
    
- El consumo de recursos se mantiene por debajo del 80 % de la capacidad de CPU, indicando margen para escalar.
    
- Los tiempos de respuesta promedio se mantuvieron dentro de los umbrales aceptables (< 2 s).
    
- La tasa de transferencia (throughput) es consistente con la capacidad de la red y el tamaño de los archivos.
    

---

## 6️⃣ Recomendaciones para escalamiento

|Área|Recomendación|
|---|---|
|**Infraestructura**|Incrementar a 2 réplicas del servicio FastAPI con balanceo Traefik.|
|**Base de datos**|Activar pooling de conexiones (20 a 50 máx) y vaciar transacciones largas.|
|**Almacenamiento**|Usar colas asincrónicas para procesar uploads grandes (Azure Queue + Celery).|
|**Caching**|Introducir Redis para consultas de detalle frecuentes.|
|**Monitoreo**|Agregar Prometheus y Grafana para analizar tiempos reales de respuesta.|
|**Próxima iteración**|Probar con 300 usuarios concurrentes y escenarios mixtos (lectura + escritura).|

---

