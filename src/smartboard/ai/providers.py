"""Gemini (primary) and Groq (fallback) providers — lazy SDK imports."""

from __future__ import annotations

from typing import Any, Callable


class GeminiProvider:
    def __init__(self, api_key: str, timeout_s: float = 2.0,
                 caller: Callable[..., str] | None = None) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required (env GEMINI_API_KEY).")
        self._api_key = api_key
        self._caller = caller
        self.timeout_s = timeout_s

    def interpret(self, transcript: str, context: dict[str, Any]) -> dict[str, str]:
        if self._caller is not None:
            return {"raw_text": self._caller(transcript, context)}
        import google.generativeai as genai  # lazy

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Convert to a board command JSON. Transcript: {transcript!r} Context: {context!r}",
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": self.timeout_s},
        )
        return {"raw_text": response.text}


class GroqProvider:
    """Live Groq provider: official SDK, JSON-object mode, 4 s timeout."""

    DEFAULT_MODEL = "openai/gpt-oss-20b"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, timeout_s: float = 4.0,
                 caller: Callable[..., str] | None = None) -> None:
        if not api_key:
            raise ValueError("AI is not configured (missing GROQ_API_KEY).")
        self._api_key = api_key
        self._model = model or self.DEFAULT_MODEL
        self._caller = caller
        self.timeout_s = timeout_s

    def interpret(self, transcript: str, context: dict[str, Any]) -> dict[str, str]:
        if self._caller is not None:
            return {"raw_text": self._caller(transcript, context)}
        from groq import Groq  # lazy

        from .prompt import build as build_prompt

        client = Groq(api_key=self._api_key, timeout=self.timeout_s)
        completion = client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": build_prompt(transcript, context)}],
            response_format={"type": "json_object"},
        )
        return {"raw_text": completion.choices[0].message.content or ""}
