"""Research node (Phase 3).

    raw_stories -> (fetch + cluster + score) -> fresh material

Currently a phase-2 stub; the real body lands with ``tools.sources``.
"""

from __future__ import annotations

from agent.graph.state import GazetteState


def research_node(state: GazetteState) -> dict:
    """Pull and score candidate stories, leaving ``raw_stories`` populated."""
    # Phase 3: call sources, cluster, score, assign to raw_stories.
    return {"raw_stories": state.get("raw_stories", [])}