"""OpenAI provider implementation for interaction analyzers."""

import json
import logging
import requests

from app.core.config import config
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Calls the OpenAI chat completions API and returns the raw model response."""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model_name = config.OPENAI_MODEL
        self.url = config.OPENAI_URL
        self.reasoning_effort = config.OPENAI_REASONING_EFFORT
        self.temperature = config.LLM_TEMPERATURE
        self.timeout = config.LLM_TIMEOUT

    def generate(self, prompt: str) -> str:
        from app.services.interaction.service import cancellation_context

        cancellation_event = cancellation_context.get()
        if cancellation_event and cancellation_event.is_set():
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "stream": True,
        }

        # Soporte para parámetro de esfuerzo de razonamiento en la familia GPT-5.6
        if "gpt-5.6" in self.model_name:
            payload["reasoning_effort"] = self.reasoning_effort

        content_parts = []

        try:
            with requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if cancellation_event and cancellation_event.is_set():
                        logger.info("OpenAI stream closed after request cancellation.")
                        response.close()
                        return ""

                    if not line or not line.startswith("data:"):
                        continue

                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        logger.debug("Ignored invalid OpenAI stream chunk.")
                        continue

                    choices = chunk.get("choices", [])
                    if not choices:
                        continue

                    text = choices[0].get("delta", {}).get("content")
                    if text:
                        content_parts.append(text)

        except requests.RequestException as exc:
            logger.error("Error communicating with OpenAI API: %s", exc)
            raise RuntimeError(f"OpenAI API request failed: {exc}")

        return "".join(content_parts).strip()