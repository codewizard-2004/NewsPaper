"""The Kernel Gazette backend agent package.

Public surface (re-exported from deeper modules):
- ``call_llm(prompt, *, task, ...)`` — provider-agnostic LLM access (core)
- ``build_graph()`` — the LangGraph StateGraph (graph)
- ``build_initial_state(date, settings)`` — a fresh run's starting state (graph)
"""

from agent.core.config import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    TASKS,
    ProviderConfig,
    resolve_config,
)
from agent.core.llm import call_llm
from agent.graph import GazetteState, build_graph, build_initial_state, newsroom_graph
from agent.schema import Issue, IssueSection, Story

__all__ = [
    # core
    "call_llm",
    "resolve_config",
    "ProviderConfig",
    "TASKS",
    "DEFAULT_PROVIDER",
    "DEFAULT_MODEL",
    # graph
    "build_graph",
    "newsroom_graph",
    "build_initial_state",
    "GazetteState",
    # schema
    "Issue",
    "IssueSection",
    "Story",
]