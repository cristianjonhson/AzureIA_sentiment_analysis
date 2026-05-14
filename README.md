# Azure IA Sentiment Analysis

Proyecto de ejemplo en Python para analizar sentimiento en español usando **Azure AI Language (Text Analytics)**.

El script procesa un texto, calcula el sentimiento general (positivo, neutral y negativo), analiza cada oración y activa **Opinion Mining** para extraer elementos evaluados y valoraciones asociadas.

## Tabla de contenido

- [Descripción del proyecto](#descripción-del-proyecto)
- [Tecnologías](#tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración](#configuración)
- [Instalación](#instalación)
- [Cómo ejecutarlo](#cómo-ejecutarlo)
- [Pruebas unitarias](#pruebas-unitarias)
- [Salida esperada](#salida-esperada)
- [Solución de problemas](#solución-de-problemas)
- [Patrones de diseño](#patrones-de-diseño)
- [Mejoras recomendadas](#mejoras-recomendadas)

## Descripción del proyecto

Este repositorio implementa un flujo básico de análisis de sentimiento con Azure:

1. Lee credenciales y endpoint desde variables de entorno.
2. Valida la configuración para evitar endpoints incorrectos.
3. Envía un documento en español al servicio de Azure AI Language.
4. Muestra:
   - Sentimiento general del documento.
   - Puntuaciones de confianza (positivo/neutral/negativo).
   - Resultados por oración.
   - Opiniones detectadas con Opinion Mining.

## Tecnologías

- Python
- Azure AI Text Analytics SDK
- Azure Core SDK

Dependencias principales (ver [requirements.txt](requirements.txt)):

- azure-ai-textanalytics
- azure-core
- requests

## Estructura del proyecto

```text
AzureIA_sentiment_analysis/
├── .gitignore
├── README.md
├── design_patterns.md
├── requirements.txt
├── sentiment_analysis.py
└── tests/
    └── test_sentiment_analysis.py
```

Archivo principal de ejecución:

- [sentiment_analysis.py](sentiment_analysis.py)

## Requisitos

- Python 3.10 o superior (recomendado)
- Cuenta de Azure con recurso **Azure AI Language**
- Credenciales del recurso:
  - `LANGUAGE_ENDPOINT`
  - `LANGUAGE_KEY`

## Configuración

### 1) Obtener endpoint y key

Desde el portal de Azure, en tu recurso de **Azure AI Language**:

- Copia el endpoint del recurso (debe iniciar con `https://`)
- Copia una de las claves de acceso

Importante:

- Usa el endpoint del recurso de Azure AI Language.
- No uses endpoints de proyecto (por ejemplo rutas con `/api/projects/...`).

### 2) Definir variables de entorno

#### macOS / Linux (bash o zsh)

```bash
export LANGUAGE_ENDPOINT="https://TU-RECURSO.cognitiveservices.azure.com/"
export LANGUAGE_KEY="TU_CLAVE"
```

#### Windows PowerShell

```powershell
$env:LANGUAGE_ENDPOINT="https://TU-RECURSO.cognitiveservices.azure.com/"
$env:LANGUAGE_KEY="TU_CLAVE"
```

## Instalación

### 1) Crear entorno virtual

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

## Cómo ejecutarlo

Con el entorno virtual activo y variables configuradas:

```bash
python sentiment_analysis.py
```

Tambien puedes pasar texto e idioma por parametros:

```bash
python sentiment_analysis.py --text "El servicio fue rapido, pero la app fallo dos veces" --language es
```

Parametros disponibles:

- `--text`: texto a analizar.
- `--language`: codigo de idioma (por ejemplo, `es`, `en`, `pt`).

## Pruebas unitarias

El proyecto incluye pruebas unitarias minimas para:

- `create_client`
- `build_documents`

Ejecucion:

```bash
python -m unittest discover -s tests -v
```

## Salida esperada

El script imprime en consola secciones similares a:

- RESULTADO GENERAL
  - sentimiento total del documento
  - puntuaciones de confianza
- RESULTADO POR ORACIÓN
  - sentimiento por oración
  - puntuaciones por oración
  - opiniones detectadas (objetivo + valoración)

## Solución de problemas

### Error: Faltan variables LANGUAGE_ENDPOINT o LANGUAGE_KEY

Define ambas variables de entorno antes de ejecutar.

### Error: LANGUAGE_ENDPOINT debe comenzar con https://

Revisa el valor del endpoint y elimina prefijos o texto extra.

### Error: Se configuró el endpoint del proyecto Foundry

Estás usando un endpoint de proyecto. Sustitúyelo por el endpoint del recurso Azure AI Language.

### Error al comunicarse con Azure Language

Verifica:

- conexión de red
- validez de la clave
- endpoint correcto
- permisos del recurso en Azure

## Patrones de diseño

En el código actual se aplican principalmente estos patrones:

- Factory (Simple Factory): centraliza la creación y validación del cliente de Azure.
- Dependency Injection (por parámetro): la función de análisis recibe el cliente en vez de crearlo internamente.
- Facade/Service Function (ligero): una función orquesta la llamada al SDK y la presentación del resultado.
- Fail Fast / Guard Clauses: validaciones tempranas para errores de configuración.
- Parameter Object Style: argumentos de entrada agrupados en `args` mediante `argparse`.
- Contrato estructural con Protocol: tipado mínimo para las puntuaciones de confianza.

En pruebas unitarias también se aplican:

- Test Double (Fake): reemplazo del SDK de Azure con clases fake para aislar pruebas.
- Fixture con Context Manager: setup/teardown encapsulado para cargar módulos fake y limpiar estado.

Patrón más apropiado para este proyecto hoy:

- Factory combinado con Dependency Injection.

Documento detallado (con justificación y ubicación exacta en código):

- [design_patterns.md](design_patterns.md)

## Mejoras recomendadas

- Leer texto desde argumentos CLI o archivo en lugar de usar texto fijo.
- Soportar múltiples documentos en una sola ejecución.
- Exportar resultados a JSON/CSV.
- Agregar pruebas unitarias para validación y parseo de respuestas.
- Agregar archivo `.env.example` y carga automática de variables con python-dotenv.

## Limpieza técnica aplicada

Se aplico una pasada de limpieza tecnica menor para mejorar mantenibilidad:

- Consistencia de organizacion: separacion de parseo de argumentos, construccion de documentos y analisis.
- Reduccion de warnings potenciales: tipado mas estricto en puntuaciones de confianza.
- Ejecucion mas flexible: soporte de parametros CLI para texto e idioma.
