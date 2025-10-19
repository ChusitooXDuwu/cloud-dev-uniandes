# Plan de pruebas 
## Descripción general
Dentro de este plan de pruebas se describirá el desarrollo y los resultados obtenidos al generar pruebas sobre la capa Web y la capa Worker del proyecto. 
## Objetivos
### Objetivo general
Determinar la capacidad máxima que soportan diferentes componentes del sistema por medio de pruebas de carga. 
### Objetivos específicos
- Generar pruebas de capacidad a la capa Web del proyecto detectando así su curva de usuarios, RPS sostenido y cuellos de botella.
- Analizar el rendimiento de la capa worker al determinar la capacidad de tamaño de videos que soporta, sus puntos de saturación y cuellos de botella. 
## Pruebas
### Escenario 1-Capa Web:
#### Descripción
Dentro del primer escenario se busca lograr determinar la cantidad máxima de usuarios concurrentes que puede soportar el API. Para esto, se desacopla la capa worker y se simula únicamente la carga de archivos. Es así como los escenarios de prueba específicos que se realizan son:
- Sanidad: en donde se utilizan 5 usuarios en 1 minuto
- Escalamiento rápida: con aumentos de 100 usuarios en 3 minutos que se mantienen por 5 minutos
- Sostenida corta: en donde se ejecuta por 5 minutos AGREGAR ACÁ NÚMERO POST PRUEBA
#### Criterios de aceptación
Para definir que los resultados son aceptables se define que la capacidad máxima debe cumplir:
- p95 de endpoints menores o iguales a 1s.
- Errores menores o iguales al 5%
- Ningún reset o timeout anómalo, ni throttling del almacenamiento.
#### Herramientas
#### Métricas 
#### Resultados

### Escenario 2-Capa Worker:
#### Descripción
#### Criterios de aceptación
#### Herramientas
#### Métricas 
#### Resultados
