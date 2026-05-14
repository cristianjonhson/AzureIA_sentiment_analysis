# Patrones de diseno en el proyecto

Este documento resume los patrones de diseno observados en el codigo actual y recomienda el patron mas apropiado para la evolucion del proyecto.

## Contexto

Archivo analizado:

- [sentiment_analysis.py](sentiment_analysis.py)

## 1) Factory (Simple Factory)

### Donde se ve

- [Funcion create_client](sentiment_analysis.py#L11)
- Construccion y retorno del cliente en [sentiment_analysis.py](sentiment_analysis.py#L36)

### Por que aplica

`create_client` encapsula la creacion de `TextAnalyticsClient` junto con validaciones de configuracion (`LANGUAGE_ENDPOINT`, `LANGUAGE_KEY`).

Esto evita repetir logica de inicializacion en varios puntos y centraliza una responsabilidad critica: crear un cliente valido para Azure AI Language.

### Beneficio en este proyecto

- Menor duplicacion.
- Mejor mantenibilidad.
- Punto unico para reforzar seguridad y validaciones.

## 2) Dependency Injection (por parametro)

### Donde se ve

- Firma de [analyze_sentiment](sentiment_analysis.py#L50)
- Inyeccion desde [main](sentiment_analysis.py#L109)

### Por que aplica

`analyze_sentiment` no crea el cliente: lo recibe como dependencia. Eso desacopla el flujo de analisis del detalle de configuracion del SDK.

### Beneficio en este proyecto

- Facilita pruebas unitarias (se puede pasar un mock/fake client).
- Reduce acoplamiento entre configuracion y logica de negocio.

## 3) Facade/Service Function (ligero)

### Donde se ve

- Orquestacion principal de analisis en [analyze_sentiment](sentiment_analysis.py#L50)

### Por que aplica

La funcion concentra la interaccion con la API externa y expone un punto de entrada de alto nivel para el caso de uso de analisis de sentimiento.

No es un Facade formal con clases, pero cumple su intencion: simplificar el uso del SDK para el resto del programa.

### Beneficio en este proyecto

- Flujo principal mas claro desde `main`.
- Menor dispersion de llamadas al SDK.

## 4) Fail Fast / Guard Clauses (patron de robustez)

### Donde se ve

- Validacion de variables requeridas en [sentiment_analysis.py](sentiment_analysis.py#L20)
- Validacion de formato de endpoint en [sentiment_analysis.py](sentiment_analysis.py#L25)
- Validacion de endpoint incorrecto (Foundry project endpoint) en [sentiment_analysis.py](sentiment_analysis.py#L30)

### Por que aplica

El codigo valida condiciones criticas al inicio y falla rapido con mensajes explicitos, evitando ejecuciones ambiguas o errores mas costosos aguas abajo.

## Patron mas apropiado para este proyecto

El patron mas apropiado para el estado actual del proyecto es:

- Factory (como base), combinado con Dependency Injection.

### Justificacion

- El principal riesgo tecnico esta en la configuracion y creacion correcta del cliente externo.
- Factory centraliza esa responsabilidad.
- Dependency Injection mantiene desacoplada la logica de analisis y deja el codigo listo para pruebas y crecimiento.

## Recomendacion de evolucion

Si el proyecto crece (API, multiples proveedores NLP, procesamiento por lotes), el siguiente patron natural es:

- Strategy

Con Strategy se podria intercambiar motor de analisis (Azure, otro proveedor o una implementacion local) sin cambiar el flujo principal del programa.
