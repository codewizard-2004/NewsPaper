"""Provider-agnostic LLM access for the Kernel Gazette.

Every LLM call in the graph goes through :func:`call_llm`. The node picks a
``task`` ("research", "edit", "write", "rate"); ``config.py`` maps that to a
provider+model. Callers never import a provider client directly.
"""

from __future__ import annotations

import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from agent.core.config import ProviderConfig, resolve_config


def _build_chat_model(cfg: ProviderConfig) -> BaseChatModel:
    """Construct the LangChain chat-model wrapper for a resolved config."""
    api_key = os.getenv(cfg.api_key_env) if cfg.api_key_env else None

    if cfg.provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=cfg.model, api_key=api_key, **cfg.extra)

    if cfg.provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=cfg.model, api_key=api_key, **cfg.extra)

    if cfg.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=cfg.model, api_key=api_key, **cfg.extra)

    if cfg.provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=cfg.model, base_url=cfg.extra.get("base_url"))

    raise ValueError(f"Unsupported provider '{cfg.provider}'")


def call_llm(prompt: str, *, task: str, model: str | None = None, system: str | None = None) -> str:
    """Send ``prompt`` to the configured LLM for ``task`` and return its text reply.

    Provider/model come from :func:`resolve_config`. Raises on failure so nodes
    can decide how to degrade gracefully.
    """
    cfg = resolve_config(task, model=model)
    chat = _build_chat_model(cfg)

    if system:
        messages = [SystemMessage(content=system), HumanMessage(content=prompt)]
    else:
        messages = [HumanMessage(content=prompt)]

    response = chat.invoke(messages)
    return _extract_text(response)


def _extract_text(response) -> str:
    content = getattr(response, "content", None)
    if content is None:
        return str(response).strip()
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(block["text"])
        return "".join(parts).strip()
    return str(content).strip()