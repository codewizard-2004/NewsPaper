import os
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.callbacks import Callbacks
from langchain_ollama import ChatOllama

_global_callbacks: Optional[List] = None

def set_global_callbacks(callbacks: List) -> None:
    global _global_callbacks
    _global_callbacks = callbacks

def get_callbacks() -> Optional[List]:
    return _global_callbacks

def get_llm(desk_name: str) -> BaseChatModel:
    """
    Factory function to return the correct LLM based on the assigned Desk.
    Currently routing all tasks to local/cloud Ollama models to save API credits.
    Available models: minimax-m3:cloud, nemotron-3-super:cloud
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    common_kwargs = {"num_ctx": 16384}
    if _global_callbacks:
        common_kwargs["callbacks"] = _global_callbacks

    # Group 1: Complex Reasoning Desks (Nemotron)
    if desk_name in ["chief_editor", "economics_desk", "ai_ml_desk", "front_desk", "security_desk"]:
        return ChatOllama(
            model="minimax-m3:cloud",
            base_url=base_url,
            temperature=0.3,
            **common_kwargs,
        )
        
    # Group 2: Creative / Niches (Minimax)
    elif desk_name in ["weather_puzzles_desk", "classifieds_desk", "obituaries_births_desk", "sports_desk", "education_desk"]:
        return ChatOllama(
            model="minimax-m3:cloud",
            base_url=base_url,
            temperature=0.7,
            **common_kwargs,
        )

    # Fallback
    return ChatOllama(
        model="minimax-m3:cloud",
        base_url=base_url,
        temperature=0.5,
        **common_kwargs,
    )
