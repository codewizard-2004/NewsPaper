"""GitHub Trending (recently-created, star-sorted) source."""

from __future__ import annotations

from datetime import datetime, timedelta

from agent.tools.base import SourceRecord, http_get_json, make_records


def fetch_github(limit: int = 5) -> list[SourceRecord]:
    """Repos created in the last week, most-starred first."""
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    data = http_get_json(
        "https://api.github.com/search/repositories"
        f"?q=created:>{last_week}&sort=stars&order=desc&per_page={limit}",
    )

    items = []
    for repo in data.get("items", []):
        items.append(
            {
                "title": repo.get("full_name"),
                "url": repo.get("html_url"),
                "score": repo.get("stargazers_count", 0),
                "summary": repo.get("description") or "",
            }
        )
    return make_records("GitHub", items)