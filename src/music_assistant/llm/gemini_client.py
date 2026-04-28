from __future__ import annotations

import json
from dataclasses import dataclass

import requests

from src.music_assistant.config import Settings


class GeminiClientError(Exception):
    """Raised when the Gemini API call fails."""


@dataclass
class GeminiClient:
    settings: Settings

    def is_enabled(self) -> bool:
        return bool(self.settings.gemini_api_key)

    def generate_json(self, prompt: str) -> dict:
        if not self.settings.gemini_api_key:
            raise GeminiClientError("GEMINI_API_KEY is not configured.")

        url = (
            f"{self.settings.gemini_base_url}/models/"
            f"{self.settings.gemini_model}:generateContent"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.settings.gemini_api_key,
            },
            json=payload,
            timeout=self.settings.llm_timeout_seconds,
        )
        if response.status_code >= 400:
            raise GeminiClientError(
                f"Gemini API request failed with status {response.status_code}: {response.text}"
            )

        body = response.json()
        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise GeminiClientError(f"Unexpected Gemini response format: {body}") from exc
