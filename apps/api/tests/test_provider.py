from unittest.mock import patch

import httpx
import pytest

from app.companion.providers import OpenRouterProvider, ProviderUnavailable
from app.core.config import Settings


def settings():
    return Settings(
        _env_file=None,
        auth_mode="demo",
        ai_provider="openrouter",
        openrouter_api_key="test-key-not-a-secret",
        openrouter_model="test/model",
    )


def test_openrouter_adapter_sends_server_side_credentials_and_output_limit():
    captured = []

    def handle(request):
        captured.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "Lesson draft"}}]})

    client = httpx.Client(transport=httpx.MockTransport(handle))
    with patch("app.companion.providers.httpx.Client", return_value=client):
        answer = OpenRouterProvider(settings()).complete([{"role": "user", "content": "Hello"}])
    assert answer == "Lesson draft"
    assert captured[0].url == "https://openrouter.ai/api/v1/chat/completions"
    assert captured[0].headers["Authorization"] == "Bearer test-key-not-a-secret"
    assert b'"max_tokens":1000' in captured[0].content
    assert b'"model":"test/model"' in captured[0].content


@pytest.mark.parametrize("status,body", [(429, {"error": "private upstream detail"}), (200, {})])
def test_provider_errors_do_not_expose_upstream_details(status, body):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(status, json=body))
    )
    with patch("app.companion.providers.httpx.Client", return_value=client):
        with pytest.raises(ProviderUnavailable) as exc:
            OpenRouterProvider(settings()).complete([{"role": "user", "content": "Hello"}])
    assert "private upstream detail" not in str(exc.value)
