"""Core infrastructure for the Kernel Gazette agent.

Provider/configuration and the provider-agnostic LLM client.
"""

from agent.core.config import ProviderConfig, TASKS, resolve_config, DEFAULT_PROVIDER, DEFAULT_MODEL

__all__ = [
    "ProviderConfig",
    "TASKS",
    "resolve_config",
    "DEFAULT_PROVIDER",
    "DEFAULT_MODEL",
]