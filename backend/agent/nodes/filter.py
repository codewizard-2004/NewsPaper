"""Filter node (Phase 3).

    fresh_stories --(seen_stories dedup)--> stays fresh; drops already-published.
"""

from __future__ import annotations

from agent.graph.state import GazetteState


def filter_node(state: GazetteState) -> dict:
    """Drop stories already published on a prior day (cross-day dedup)."""
    # Phase 3 stub)
    return {}