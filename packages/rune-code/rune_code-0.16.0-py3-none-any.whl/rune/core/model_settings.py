# src/rune/core/model_settings.py
from collections.abc import Mapping
from typing import Any

from pydantic_ai.models.anthropic import AnthropicModelSettings
from pydantic_ai.models.google import GoogleModelSettings
from pydantic_ai.models.groq import GroqModelSettings
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

# …import other providers as you need them

_PROVIDER_MAP = {
    "google": GoogleModelSettings,
    "openai": OpenAIResponsesModelSettings,
    "anthropic": AnthropicModelSettings,
    "groq": GroqModelSettings,
    "azure": OpenAIResponsesModelSettings,
    # add more here
}


def build_settings(model_name: str, overrides: Mapping[str, Any] | None = None):
    """
    Return an appropriate *ModelSettings* instance for `model_name`.

    `overrides` is an optional dict of kwargs forwarded to the settings
    constructor (useful for flags like temperature, thinking configs, etc.).
    """
    provider = model_name.split(":", 1)[0]  # e.g. "google-vertex" → "google"
    provider = provider.split("-", 1)[0]  # strip "-vertex", "-gla", etc.
    cls = _PROVIDER_MAP.get(provider)
    if cls is None:  # fall back to a generic base class
        return None
    if provider == "google":
        overrides = {
            "google_thinking_config": {
                "include_thoughts": True,
                "thinking_budget": 32768,
            },
            **(overrides or {}),
        }
    elif provider in {"openai", "azure"}:
        overrides = {
            "openai_reasoning_effort": "high",
            "openai_reasoning_summary": "concise",
            **(overrides or {}),
        }
    return cls(**(overrides or {}))
