from __future__ import annotations

import argparse
import os
import sys
from typing import Protocol

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError


DEFAULT_TEXT = (
    "La atencion del personal fue excelente y resolvieron rapidamente "
    "mi solicitud. Sin embargo, la aplicacion presento varios errores "
    "y tardo demasiado en cargar."
)
DEFAULT_LANGUAGE = "es"


class ConfidenceScoresLike(Protocol):
    positive: float
    neutral: float
    negative: float


def create_client() -> TextAnalyticsClient:
    """Crea el cliente de Azure Language usando variables de entorno."""
    endpoint = os.getenv("LANGUAGE_ENDPOINT", "").strip()
    key = os.getenv("LANGUAGE_KEY", "").strip()

    # Elimina accidentalmente comillas copiadas dentro del valor.
    endpoint = endpoint.strip("\"'“”")
    key = key.strip("\"'“”")

    if not endpoint or not key:
        raise RuntimeError(
            "Faltan las variables LANGUAGE_ENDPOINT o LANGUAGE_KEY."
        )

    if not endpoint.startswith("https://"):
        raise RuntimeError(
            "LANGUAGE_ENDPOINT debe comenzar con https://"
        )

    if "/api/projects/" in endpoint:
        raise RuntimeError(
            "Se configuró el endpoint del proyecto Foundry. "
            "Utiliza el endpoint del recurso Azure AI Language."
        )

    return TextAnalyticsClient(
        endpoint=endpoint.rstrip("/"),
        credential=AzureKeyCredential(key),
    )


def parse_args() -> argparse.Namespace:
    """Parsea argumentos opcionales para texto e idioma."""
    parser = argparse.ArgumentParser(
        description="Analiza sentimiento con Azure AI Language."
    )
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help="Texto a analizar.",
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help="Codigo de idioma del texto (ejemplo: es, en).",
    )
    return parser.parse_args()


def show_scores(title: str, scores: ConfidenceScoresLike) -> None:
    """Muestra las puntuaciones de confianza como porcentajes."""
    print(title)
    print(f"  Positivo: {scores.positive * 100:.2f} %")
    print(f"  Neutral:  {scores.neutral * 100:.2f} %")
    print(f"  Negativo: {scores.negative * 100:.2f} %")


def build_documents(text: str, language: str) -> list[dict[str, str]]:
    """Construye la lista de documentos para Azure AI Language."""
    return [
        {
            "id": "documento-1",
            "language": language,
            "text": text,
        }
    ]


def analyze_sentiment(
    client: TextAnalyticsClient,
    text: str,
    language: str,
) -> None:
    """Analiza el sentimiento y las opiniones presentes en un texto."""
    documents = build_documents(text=text, language=language)

    results = client.analyze_sentiment(
        documents=documents,
        show_opinion_mining=True,
    )

    if not results:
        print("No se recibieron resultados del servicio.")
        return

    document = results[0]

    if document.is_error:
        print(f"Error del documento: {document.error.code}")
        print(document.error.message)
        return

    print("\n=== RESULTADO GENERAL ===")
    print(f"Sentimiento: {document.sentiment}")
    show_scores("Puntuaciones generales:", document.confidence_scores)

    print("\n=== RESULTADO POR ORACIÓN ===")

    for number, sentence in enumerate(document.sentences, start=1):
        print(f"\nOración {number}: {sentence.text}")
        print(f"Sentimiento: {sentence.sentiment}")
        show_scores("Puntuaciones:", sentence.confidence_scores)

        if sentence.mined_opinions:
            print("Opiniones identificadas:")

        for opinion in sentence.mined_opinions:
            target = opinion.target

            print(
                f"  Elemento evaluado: '{target.text}' "
                f"({target.sentiment})"
            )

            for assessment in opinion.assessments:
                print(
                    f"    Valoración: '{assessment.text}' "
                    f"({assessment.sentiment})"
                )


def main() -> None:
    args = parse_args()

    try:
        client = create_client()
        analyze_sentiment(
            client=client,
            text=args.text,
            language=args.language,
        )

    except RuntimeError as error:
        print(f"Error de configuración: {error}")
        sys.exit(1)

    except AzureError as error:
        print(f"Error al comunicarse con Azure Language: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
