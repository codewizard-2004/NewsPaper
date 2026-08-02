"""Reddit source (r/technology + r/programming)."""

from __future__ import annotations

from agent.tools.base import SourceRecord, http_get_json, make_records

SUBREDDITS = ("technology", "programming")


def fetch_reddit(limit: int = 5) -> list[SourceRecord]:
    """Top posts of the day from the tech subreddits."""
    items = []
    for subreddit in SUBREDDITS:
        data = http_get_json(
            f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day",
        )
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            if post.get("url"):
                items.append(
                    {
                        "title": post.get("title"),
                        "url": post.get("url"),
                        "score": post.get("score", 0),
                    }
                )
    return make_records("Reddit", items)