from __future__ import annotations

import importlib
import os
import sys
import types
import unittest
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def fake_azure_modules():
    saved_modules = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name == "azure" or name.startswith("azure.")
    }

    for name in list(sys.modules):
        if name == "azure" or name.startswith("azure."):
            del sys.modules[name]

    azure_module = types.ModuleType("azure")
    azure_ai_module = types.ModuleType("azure.ai")
    azure_textanalytics_module = types.ModuleType("azure.ai.textanalytics")
    azure_core_module = types.ModuleType("azure.core")
    azure_core_credentials_module = types.ModuleType("azure.core.credentials")
    azure_core_exceptions_module = types.ModuleType("azure.core.exceptions")

    class FakeTextAnalyticsClient:
        def __init__(self, endpoint: str, credential: object) -> None:
            self.endpoint = endpoint
            self.credential = credential

    class FakeAzureKeyCredential:
        def __init__(self, key: str) -> None:
            self.key = key

    class FakeAzureError(Exception):
        pass

    azure_textanalytics_module.TextAnalyticsClient = FakeTextAnalyticsClient
    azure_core_credentials_module.AzureKeyCredential = FakeAzureKeyCredential
    azure_core_exceptions_module.AzureError = FakeAzureError

    azure_module.ai = azure_ai_module
    azure_ai_module.textanalytics = azure_textanalytics_module
    azure_module.core = azure_core_module
    azure_core_module.credentials = azure_core_credentials_module
    azure_core_module.exceptions = azure_core_exceptions_module

    fake_modules = {
        "azure": azure_module,
        "azure.ai": azure_ai_module,
        "azure.ai.textanalytics": azure_textanalytics_module,
        "azure.core": azure_core_module,
        "azure.core.credentials": azure_core_credentials_module,
        "azure.core.exceptions": azure_core_exceptions_module,
    }

    sys.modules.update(fake_modules)

    try:
        yield FakeTextAnalyticsClient, FakeAzureKeyCredential
    finally:
        for name in list(sys.modules):
            if name == "azure" or name.startswith("azure."):
                del sys.modules[name]
        sys.modules.update(saved_modules)


@contextmanager
def loaded_module():
    module_name = "sentiment_analysis"
    previous = sys.modules.get(module_name)
    if module_name in sys.modules:
        del sys.modules[module_name]

    with fake_azure_modules() as fake_classes:
        module = importlib.import_module(module_name)
        try:
            yield module, fake_classes
        finally:
            if module_name in sys.modules:
                del sys.modules[module_name]
            if previous is not None:
                sys.modules[module_name] = previous


class CreateClientTests(unittest.TestCase):
    def test_create_client_fails_if_required_env_is_missing(self) -> None:
        with loaded_module() as (module, _):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(RuntimeError) as context:
                    module.create_client()

        self.assertIn("Faltan las variables LANGUAGE_ENDPOINT", str(context.exception))

    def test_create_client_fails_if_endpoint_is_not_https(self) -> None:
        with loaded_module() as (module, _):
            with patch.dict(
                os.environ,
                {
                    "LANGUAGE_ENDPOINT": "http://example.test",
                    "LANGUAGE_KEY": "key-test",
                },
                clear=True,
            ):
                with self.assertRaises(RuntimeError) as context:
                    module.create_client()

        self.assertIn("debe comenzar con https://", str(context.exception))

    def test_create_client_fails_if_endpoint_points_to_project_path(self) -> None:
        with loaded_module() as (module, _):
            with patch.dict(
                os.environ,
                {
                    "LANGUAGE_ENDPOINT": "https://example.test/api/projects/demo",
                    "LANGUAGE_KEY": "key-test",
                },
                clear=True,
            ):
                with self.assertRaises(RuntimeError) as context:
                    module.create_client()

        self.assertIn("endpoint del proyecto Foundry", str(context.exception))

    def test_create_client_returns_client_with_sanitized_values(self) -> None:
        with loaded_module() as (module, fake_classes):
            fake_client_class, fake_credential_class = fake_classes
            with patch.dict(
                os.environ,
                {
                    "LANGUAGE_ENDPOINT": "'https://example.cognitiveservices.azure.com/'",
                    "LANGUAGE_KEY": '"key-value"',
                },
                clear=True,
            ):
                client = module.create_client()

        self.assertIsInstance(client, fake_client_class)
        self.assertEqual(client.endpoint, "https://example.cognitiveservices.azure.com")
        self.assertIsInstance(client.credential, fake_credential_class)
        self.assertEqual(client.credential.key, "key-value")


class BuildDocumentsTests(unittest.TestCase):
    def test_build_documents_returns_expected_payload(self) -> None:
        with loaded_module() as (module, _):
            payload = module.build_documents(
                text="Texto de prueba",
                language="es",
            )

        self.assertEqual(
            payload,
            [
                {
                    "id": "documento-1",
                    "language": "es",
                    "text": "Texto de prueba",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
