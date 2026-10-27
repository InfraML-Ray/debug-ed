from typing import Protocol

import httpx

from app.core.config import Settings


class ProviderUnavailable(Exception):
    pass


class ChatProvider(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class DemoProvider:
    def complete(self, messages: list[dict[str, str]]) -> str:
        return (
            "Demo response — no AI model was called.\n\n"
            "Here is an example lesson structure you can adapt:\n"
            "1. Start with a question that checks prior knowledge (5 minutes).\n"
            "2. Explain one learning objective using a worked example (10 minutes).\n"
            "3. Let learners practise in pairs, with support where needed (15 minutes).\n"
            "4. Finish with an exit ticket and review misconceptions (10 minutes).\n\n"
            "This is a fixed example, not an answer grounded in your curriculum."
        )


class OpenRouterProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def complete(self, messages: list[dict[str, str]]) -> str:
        api_key = self.settings.openrouter_api_key.get_secret_value()
        try:
            with httpx.Client(timeout=httpx.Timeout(45, connect=5)) as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": self.settings.openrouter_model,
                        "messages": messages,
                        "max_tokens": self.settings.ai_max_output_tokens,
                        "temperature": 0.4,
                    },
                )
                response.raise_for_status()
                answer = response.json()["choices"][0]["message"]["content"]
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError("Empty provider response")
                return answer
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            # Provider bodies can contain sensitive request details; do not expose them.
            raise ProviderUnavailable("The AI provider is unavailable. Please try again.") from exc


def build_provider(settings: Settings) -> ChatProvider:
    if settings.ai_provider == "openrouter":
        return OpenRouterProvider(settings)
    return DemoProvider()
