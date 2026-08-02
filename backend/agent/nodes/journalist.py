"""Journalist nodes (Phase 5) -- one per page bucket, run in parallel.

Each journalist writes full article text plus ``confidence_rating`` +
``importance_rating`` for its page's stories. The Misc journalist also owns
DSA and the comic storyline.
"""

from __future__ import annotations

from agent.graph.state import GazetteState

# Page buckets the Editor writes and journalists consume.
PAGES = ("front_page", "aiml_page", "security_page", "misc_page")

# Journalist node names, one per page bucket.
JOURNALIST_NODES = {page: f"journalist_{page}" for page in PAGES}


def build_journalist(page: str):
    """Return the journalist node body for ``page`` (currently a stub).

    Phase 5 replaces the stub per page (the Misc journalist additionally
    handles DSA + comic). Returns Firestore-shaped article item dicts.
    """

    def journalist_node(state: GazetteState) -> dict:
        categorized = state.get("categorized") or {}
        items = []
        for story in categorized.get(page, []):
            items.append(
                {
                    "id": story.get("url", "")[-8:] or "x",
                    "type": "article",
                    "headline": story.get("title", ""),
                    "body": story.get("body") or "",
                    "sources": story.get("cluster_sources", []),
                    "confidence_rating": story.get("confidence_rating", 0.0),
                    "importance_rating": story.get("importance_rating", 0.0),
                    "image_url": None,
                }
            )
        return {"items": items}

    return journalist_node