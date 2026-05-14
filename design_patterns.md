# Patrones de diseno en el proyecto

Este documento resume los patrones de diseno observados en el estado actual del repositorio y distingue entre patrones aplicados en codigo de aplicacion y en pruebas.

## Contexto

Archivos analizados:

- [sentiment_analysis.py](sentiment_analysis.py)
- [tests/test_sentiment_analysis.py](tests/test_sentiment_analysis.py)

## Patrones en codigo de aplicacion

## 1) Factory (Simple Factory)

### Donde se ve

- [Funcion create_client](sentiment_analysis.py#L27)
- Construccion y retorno del cliente en [sentiment_analysis.py](sentiment_analysis.py#L52)

### Por que aplica

`create_client` encapsula la creacion de `TextAnalyticsClient` junto con validaciones de configuracion (`LANGUAGE_ENDPOINT`, `LANGUAGE_KEY`).

### Beneficio en este proyecto

- Menor duplicacion.
- Mejor mantenibilidad.
- Punto unico para reforzar seguridad y validaciones.

## 2) Dependency Injection (por parametro)

### Donde se ve

- Firma de [analyze_sentiment](sentiment_analysis.py#L95)
- Inyeccion desde [main](sentiment_analysis.py#L152)

### Por que aplica

`analyze_sentiment` no crea el cliente: lo recibe como dependencia. Eso desacopla el flujo de analisis del detalle de configuracion del SDK.

### Beneficio en este proyecto

- Facilita pruebas unitarias.
- Reduce acoplamiento entre configuracion y logica de negocio.

## 3) Facade/Service Function (ligero)

### Donde se ve

- Orquestacion principal de analisis en [analyze_sentiment](sentiment_analysis.py#L95)

### Por que aplica

La funcion concentra la interaccion con la API externa y expone un punto de entrada de alto nivel para el caso de uso de analisis de sentimiento.

## 4) Fail Fast / Guard Clauses

### Donde se ve

- Validacion de variables requeridas en [sentiment_analysis.py](sentiment_analysis.py#L36)
- Validacion de formato de endpoint en [sentiment_analysis.py](sentiment_analysis.py#L41)
- Validacion de endpoint incorrecto en [sentiment_analysis.py](sentiment_analysis.py#L46)
- Validacion de resultados vacios en [sentiment_analysis.py](sentiment_analysis.py#L108)

### Por que aplica

El codigo valida condiciones criticas al inicio y falla rapido con mensajes explicitos, evitando ejecuciones ambiguas o errores mas costosos.

## 5) Parameter Object Style (configuracion de entrada)

### Donde se ve

- Parseo y agrupacion de parametros en [parse_args](sentiment_analysis.py#L58)
- Uso de `args` en [main](sentiment_analysis.py#L149)

### Por que aplica

La entrada de ejecucion se centraliza en un objeto de argumentos, mejorando legibilidad y evolucion del CLI.

## 6) Interface por contrato estructural (Protocol)

### Donde se ve

- Definicion de contrato en [ConfidenceScoresLike](sentiment_analysis.py#L21)
- Uso en [show_scores](sentiment_analysis.py#L76)

### Por que aplica

Se define un contrato minimo de atributos esperados para reducir warnings de tipado y desacoplar la funcion de una clase concreta del SDK.

## Patrones en pruebas unitarias

## 7) Test Double (Fake)

### Donde se ve

- Fakes del SDK en [tests/test_sentiment_analysis.py](tests/test_sentiment_analysis.py#L31)

### Por que aplica

Permite probar la logica propia sin depender de red, credenciales reales ni comportamiento externo del servicio.

## 8) Fixture con Context Manager

### Donde se ve

- Preparacion/limpieza de modulos fake en [fake_azure_modules](tests/test_sentiment_analysis.py#L13)
- Carga aislada del modulo bajo prueba en [loaded_module](tests/test_sentiment_analysis.py#L74)

### Por que aplica

Encapsula setup/teardown de pruebas para mantener aislamiento entre casos y evitar efectos laterales globales.

## Patron mas apropiado para el proyecto

Para el estado actual, el patron mas apropiado sigue siendo:

- Factory combinado con Dependency Injection.

### Justificacion

- El principal riesgo tecnico sigue en la configuracion y creacion correcta del cliente externo.
- Factory centraliza esa responsabilidad.
- Dependency Injection mantiene desacoplada la logica de analisis y habilita pruebas simples.

## Recomendacion de evolucion

Si el proyecto crece (API, multiples proveedores NLP, procesamiento por lotes), el siguiente patron natural es:

- Strategy

Con Strategy se podria intercambiar motor de analisis (Azure, otro proveedor o una implementacion local) sin cambiar el flujo principal del programa.
