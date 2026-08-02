"""Filter node.

Phase 3: cross the raw stories against ``seen_stories`` and drop anything already
published on a prior day. Pure Firestore lookup, no LLM, no sentence detection.

Output: ``fresh_stories: List[dict]``.

If Firestore is unreachable (no credentials / network), we degrade to keeping
all stories rather than failing the run or dropping everything.
"""

from __future__ import annotations

from agent.graph.state import GazetteState
from firebase.seen import get_seen


def _already_seen(url: str) -> bool:
    """Returned True if this canonical URL was published on a prior day."""
    try:
        return get_seen(url)
    except Exception:  # noqa: BLE001 - a failed lookup must not drop the story
        return False


def filter_node(state: GazetteState) -> dict:
    raw = state.get("raw_stories") or []
    fresh = [story for story in raw if not _already_seen(story.get("url", ""))]
    return {"fresh_stories": fresh}