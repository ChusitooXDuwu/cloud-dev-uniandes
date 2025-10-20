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


### Escenario 2-Capa Worker:
#### Descripción
Dentro de este escenario se busca realizar pruebas sobre la capa worker, para esto se busca ver cuantos videos se procesan por minuto en la aplicación. Esto permite ver que tan bueno es el desempeño del worker. Nuevamente es de mencionar que los resultados se podrán ver afectados por las especificaciones de la máquina, por lo que al momento de desplegar el servicio en nube, los resultados pueden cambiar. 
#### Criterios de aceptación
Para determinar si la prueba fue exitosa o no se utiliza la capacidad nominal que se refiere a los videos procesados por minuto y la estabilidad, la cual dice si la cola no crece sin control. 
#### Herramientas
Para estas pruebas se utilizaron scripts de python en donde se realiza el proceso de mandar información directamente al worker y guardar las métricas de tiempos.  
#### Resultados
