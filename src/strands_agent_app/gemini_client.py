import json
from typing import Any

import requests

from .config import settings


class GeminiClient:
    def __init__(self, api_key: str | None = None, endpoint: str | None = None, temperature: float | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.endpoint = endpoint or settings.gemini_url
        self.temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env or the environment.")

    def _build_payload(self, user_message: str, system_message: str) -> dict[str, Any]:
        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_message}\n\n{user_message}",
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
            },
        }

    def chat(self, user_message: str, system_message: str | None = None) -> str:
        system_message = system_message or (
            "You are a customer feedback assistant. Summarize Amazon.in review content clearly, "
            "highlighting positive points, issues, and sentiment."
        )
        payload = self._build_payload(user_message, system_message)
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        parsed = response.json()

        text = self._extract_text(parsed)
        if text:
            return text.strip()

        return json.dumps(parsed, indent=2)

    def _extract_text(self, data: dict[str, Any]) -> str | None:
        candidates = data.get("candidates")
        if isinstance(candidates, list) and candidates:
            first = candidates[0]
            if isinstance(first, dict):
                content = first.get("content")
                if isinstance(content, dict):
                    parts = content.get("parts")
                    if isinstance(parts, list) and parts:
                        first_part = parts[0]
                        if isinstance(first_part, dict) and "text" in first_part:
                            return first_part["text"]
        return None
