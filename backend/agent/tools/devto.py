"""Dev.to source."""

from __future__ import annotations

from agent.tools.base import SourceRecord, http_get_json, make_records


def fetch_dev_to(limit: int = 5) -> list[SourceRecord]:
    """Top articles on Dev.to (reactions used as score)."""
    data = http_get_json(f"https://dev.to/api/articles?top=1&per_page={limit}")

    items = []
    for post in data:
        if post.get("url"):
            items.append(
                {
                    "title": post.get("title"),
                    "url": post.get("url"),
                    "score": post.get("public_reactions_count", 0),
                    "summary": (post.get("description") or "")[:280],
                }
            )
    return make_records("Dev.to", items)