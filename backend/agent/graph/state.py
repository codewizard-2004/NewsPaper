"""Shared state for the Kernel Gazette graph.

This is the whiteboard passed between nodes. Flow (per ``agents.md``):

    Research -> Filter -> Editor -> journalists (parallel) -> Publisher
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, List, Optional, TypedDict

# A story flowing through the pipeline; the pydantic shape is in ``agent.schema.story``.
Story = dict[str, Any]

# One published article (or DSA/comic item) inside the final issue (see ``agent.schema``).
Item = dict[str, Any]

# page bucket -> list of stories selected for it
Categorized = dict[str, List[Story]]


class GazetteState(TypedDict):
    date: str
    settings: dict

    # Research / Filter
    raw_stories: List[Story]
    fresh_stories: List[Story]

    # Editor
    categorized: Optional[Categorized]

    # Journalists (accumulated across parallel nodes)
    items: Annotated[List[Item], operator.add]
    errors: Annotated[List[dict], operator.add]

    # Publisher
    issue: Optional[dict]


def build_initial_state(date: str, settings: dict | None = None) -> GazetteState:
    return {
        "date": date,
        "settings": settings or {},
        "raw_stories": [],
        "fresh_stories": [],
        "categorized": None,
        "items": [],
        "errors": [],
        "issue": None,
    }