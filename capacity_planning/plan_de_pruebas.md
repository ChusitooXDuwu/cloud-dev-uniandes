# Plan de pruebas 
## Descripción general
Dentro de este plan de pruebas se describirá el desarrollo y los resultados obtenidos al generar pruebas sobre la capa Web y la capa Worker del proyecto. 
## Objetivos
### Objetivo general
Determinar la capacidad máxima que soportan diferentes componentes del sistema por medio de pruebas de carga. 
### Objetivos específicos
- Generar pruebas de capacidad a la capa Web del proyecto detectando así su curva de usuarios, RPS sostenido y cuellos de botella.
- Analizar el rendimiento de la capa worker al determinar la capacidad de tamaño de videos que soporta, sus puntos de saturación y cuellos de botella.
## Configuración del sistema
Para realizar las pruebas a esta aplicación, se utilizará una maquina con 16GB de RAM y 6 núcleos. Con esto, se tendrá una idea del desempeño del sistema de forma local con especificaciones medianas. Más adelante al hacer uso de instancias de AWS, los resultados que se presentan dentro de estas pruebas pueden no ser iguales debido a los cambios que se presenten debido a los recursos de las máquinas. 
## Pruebas
### Escenario 1-Capa Web:
#### Descripción
Dentro del primer escenario se busca lograr determinar la cantidad máxima de usuarios concurrentes que puede soportar el API. Para esto, se desacopla la capa worker y se simula únicamente la carga de archivos. Es así como los escenarios de prueba específicos que se realizan son:
- Sanidad: en donde se utilizan 5 usuarios en 1 minuto
- Escalamiento rápida: con aumentos de 100 usuarios en 3 minutos que se mantienen por 5 minutos
- Sostenida corta: en donde se ejecuta por 5 minutos AGREGAR ACÁ NÚMERO POST PRU

Cabe resaltar que para este escenario no se incluye el efecto de la capa Worker, por lo que para generar estos resultados se hicieron leves modificaciones al código que se presenta, en donde la capa Worker no realiza ningún proceso y solo manda una respuesta de éxito. 
#### Criterios de aceptación
Para definir que los resultados son aceptables se define que la capacidad máxima debe cumplir:
- p95 de endpoints menores o iguales a 1s.
- Errores menores o iguales al 5%
- Ningún reset o timeout anómalo, ni throttling del almacenamiento.
#### Herramientas
Como herramientas para el desarrollo de estas pruebas se utilizó locust, Prometheus + Grafana y APM. Los archivo locust utilizados para estas pruebas se identifican como `locust_web.py` y el nombre de la prueba dentro de la carpeta pruebas_capa_web. 
#### Resultados
A partir de la ejecución de pruebas de capa web, se pudieron obtener los siguientes resultados:
A partir de la ejecución de pruebas de capa web, se pudieron obtener los siguientes resultados:
##### Smoke:
En cuanto a la prueba smoke, esta se realizó con 5 usuarios en tiempos de 1 minuto. Como se puede ver en la imagen, esto no genero ningún fallo en ninguna de las peticiones permitiendo ver así como el proceso fue exitoso. Adicionalmente, al revisar los resultados de las gráficas se puede ver que el RPS oscila la mayoría del tiempo entre 3 y 4. El tiempo de respuesta del percentil 95 se encuentra sobre los 3.25 segundos y el número de usuarios muestra como se cumplió con que los 5 usuarios llegaran, se mantuvieran por un periodo de tiempo y luego desaparecieran. Dentro de la carpeta de resultados se incluyen l
##### Ramp:
Para estas pruebas se aumentó gradualmente la carga de usuarios en el sistema. Se pudo observar que al llegar a 500 se detecta un 3% de errores. SIn embargo, con 600 usuarios el sistema falla totalmente y tiene errores de más del 90%. Es por esto que el punto estable de la aplicación es hasta 500 usuarios. Esto se puede ver en las gráficas de resultados anexas dentro de la carpeta de resultados. 
##### Sostenida:
Finalmente, para esta prueba se utilizó la información de que la aplicación soporta un máximo de 500 usuarios y se realizó una prueba sostenida por 5 minutos con el 80% de esta carga. Siendo así, se pudo ver que esto cumple limites de error al tener solo el 4% de fallas en el sistema, no se presentan problemas de resets o timeouts y se reporta un RPS agregado de 118.9, lo que significa que se pueden procesar esa cantidad de solicitudes por segundo. 

### Escenario 2-Capa Worker:
#### Descripción
Dentro de este escenario se busca realizar pruebas sobre la capa worker, para esto se busca ver cuantos videos se procesan por minuto en la aplicación. Esto permite ver que tan bueno es el desempeño del worker. Nuevamente es de mencionar que los resultados se podrán ver afectados por las especificaciones de la máquina, por lo que al momento de desplegar el servicio en nube, los resultados pueden cambiar. 
#### Criterios de aceptación
Para determinar si la prueba fue exitosa o no se utiliza la capacidad nominal que se refiere a los videos procesados por minuto y la estabilidad, la cual dice si la cola no crece sin control. 
#### Herramientas
Para estas pruebas se utilizaron scripts de python en donde se realiza el proceso de mandar información directamente al worker y guardar las métricas de tiempos.  
#### Resultados
A partir de los resultados de las pruebas se puede ver los siguientes resultados de la prueba de saturación. En general, los resultados muestran que se logra procesar una cantidad adecuada de videos dentro de celery en un tiempo pequeño. A continuación, se presenta una tabla con los resultados que están almacenados en un csv dentro de la carpeta de resultados. 
| video_size_mb | concurrency | total_videos | elapsed_seconds | throughput_videos_per_min | start_time                  | end_time                    |
|----------------|--------------|---------------|-----------------|----------------------------|------------------------------|------------------------------|
| 50             | 1            | 10            | 28.2            | 10.64                      | 2025-10-19 23:24:14.699008   | 2025-10-19 23:24:42.903723   |
| 50             | 2            | 10            | 50.9            | 5.89                       | 2025-10-19 23:24:42.904455   | 2025-10-19 23:25:33.807365   |
| 50             | 4            | 10            | 48.78           | 6.15                       | 2025-10-19 23:25:33.808469   | 2025-10-19 23:26:22.589445   |
| 100            | 1            | 10            | 50.99           | 5.88                       | 2025-10-19 23:26:22.590090   | 2025-10-19 23:27:13.581750   |
| 100            | 2            | 10            | 50.92           | 5.89                       | 2025-10-19 23:27:13.582656   | 2025-10-19 23:28:04.507364   |
| 100            | 4            | 10            | 48.92           | 6.13                       | 2025-10-19 23:28:04.508417   | 2025-10-19 23:28:53.425889   |

