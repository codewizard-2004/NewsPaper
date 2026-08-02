"""Publisher node (Phase 6).

    items --(confidence filter, fold thin sections, images)--> issue -> Firestore.
"""

from __future__ import annotations

from agent.graph.state import GazetteState


def publisher_node(state: GazetteState) -> dict:
    """Assemble and write today's issue (currently a stub)."""
    # Phase 6 stub: build issue from state["items"], write issues/{date}.
    return {"issue": None}