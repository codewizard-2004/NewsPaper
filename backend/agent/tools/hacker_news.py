"""Hacker News source."""

from __future__ import annotations

from agent.tools.base import SourceRecord, http_get_json, make_records


def fetch_hacker_news(limit: int = 8) -> list[SourceRecord]:
    """Top linked stories (real links only — skips Ask HN / polls)."""
    top_ids = http_get_json(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
    )[:limit]

    items = []
    for sid in top_ids:
        story = http_get_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if story.get("url"):
            items.append(
                {
                    "title": story.get("title"),
                    "url": story.get("url"),
                    "score": story.get("score", 0),
                }
            )
    return make_records("Hacker News", items)