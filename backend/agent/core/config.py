"""Configuration for the Kernel Gazette agent graph.

Env-driven mapping from task -> (provider, model). Everything that varies
between providers lives here; ``llm.py`` stays provider-agnostic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

# Valid tasks -- the "why" behind a call, used to pick a provider/model.
TASKS = ("research", "edit", "write", "rate")

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "gemini").strip() or "gemini"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3.5-flash-lite").strip() or "gemini-3.5-flash-lite"

# Publisher thresholds (env-driven; see .env.example).
PUBLISHER_CONFIDENCE_THRESHOLD = float(os.getenv("PUBLISHER_CONFIDENCE_THRESHOLD", "0.5"))
PUBLISHER_MIN_PAGE_ITEMS = int(os.getenv("PUBLISHER_MIN_PAGE_ITEMS", "3"))
PUBLISHER_IMAGE_IMPORTANCE = float(os.getenv("PUBLISHER_IMAGE_IMPORTANCE", "7.0"))

# provider -> env var holding its API key (ollama needs none)
API_KEY_ENV = {
    "gemini": "GOOGLE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

# provider -> sensible default model
DEFAULT_MODELS = {
    "gemini": "gemini-3.5-flash-lite",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "ollama": "llama3.1:70b",
}


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    api_key_env: str | None = None
    extra: dict = field(default_factory=dict)


def _task_env(task: str, suffix: str) -> str | None:
    value = os.getenv(f"AGENT_TASK_{task.upper()}_{suffix}")
    return (value or "").strip() or None


def resolve_config(task: str, model: str | None = None) -> ProviderConfig:
    """Resolve the provider+model for ``task``.

    Precedence for model: explicit ``model`` arg > per-task env > provider default.
    """
    task = task.lower()
    if task not in TASKS:
        raise ValueError(f"Unknown task '{task}'. Valid tasks: {', '.join(TASKS)}")

    provider = _task_env(task, "PROVIDER") or DEFAULT_PROVIDER
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unsupported provider '{provider}'. Choose from {list(DEFAULT_MODELS)}")

    chosen_model = model or _task_env(task, "MODEL") or DEFAULT_MODEL or DEFAULT_MODELS[provider]

    extra: dict = {}
    api_key_env = API_KEY_ENV.get(provider)

    if provider == "ollama":
        extra["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        # Ollama Cloud needs no API key.
        api_key_env = None

    return ProviderConfig(
        provider=provider,
        model=chosen_model,
        api_key_env=api_key_env,
        extra=extra,
    )