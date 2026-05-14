from __future__ import annotations

import os
import sys

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError


def create_client() -> TextAnalyticsClient:
    """Crea el cliente de Azure Language usando variables de entorno."""
    endpoint = os.getenv("LANGUAGE_ENDPOINT")
    key = os.getenv("LANGUAGE_KEY")

    if not endpoint or not key:
        raise RuntimeError(
            "Faltan las variables LANGUAGE_ENDPOINT o LANGUAGE_KEY."
        )

    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def show_scores(title: str, scores: object) -> None:
    """Muestra las puntuaciones de confianza como porcentajes."""
    print(title)
    print(f"  Positivo: {scores.positive * 100:.2f} %")
    print(f"  Neutral:  {scores.neutral * 100:.2f} %")
    print(f"  Negativo: {scores.negative * 100:.2f} %")


def analyze_sentiment(client: TextAnalyticsClient, text: str) -> None:
    """Analiza el sentimiento y las opiniones presentes en un texto."""
    documents = [
        {
            "id": "documento-1",
            "language": "es",
            "text": text,
        }
    ]

    results = client.analyze_sentiment(
        documents=documents,
        show_opinion_mining=True,
    )

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
    text = (
        "La atención del personal fue excelente y resolvieron rápidamente "
        "mi solicitud. Sin embargo, la aplicación presentó varios errores "
        "y tardó demasiado en cargar."
    )

    try:
        client = create_client()
        analyze_sentiment(client, text)

    except RuntimeError as error:
        print(f"Error de configuración: {error}")
        sys.exit(1)

    except AzureError as error:
        print(f"Error al comunicarse con Azure Language: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
