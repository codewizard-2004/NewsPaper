"""Source tool orchestrator.

Runs all feed sources (in parallel), collects their normalized records, and
returns a flat list. No dedup here — Research node merges clusters.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from agent.tools.base import SourceRecord
from agent.tools.devto import fetch_dev_to
from agent.tools.github import fetch_github as fetch_github_trending
from agent.tools.hacker_news import fetch_hacker_news
from agent.tools.reddit import fetch_reddit
from agent.tools.techcrunch import fetch_techcrunch
from agent.tools.theverge import fetch_the_verge

# Name -> fetcher. Each returns list[SourceRecord].
FETCHERS: dict[str, Callable[[int], list[SourceRecord]]] = {
    "Hacker News": fetch_hacker_news,
    "Reddit": fetch_reddit,
    "Dev.to": fetch_dev_to,
    "GitHub": fetch_github_trending,
    "TechCrunch": fetch_techcrunch,
    "The Verge": fetch_the_verge,
}


def fetch_all_sources(limit: int = 5) -> list[SourceRecord]:
    """Run every source in parallel; each failure yields an empty list (never raises)."""
    records: list[SourceRecord] = []
    with ThreadPoolExecutor(max_workers=len(FETCHERS)) as pool:
        futures = {pool.submit(fn, limit): name for name, fn in FETCHERS.items()}
        for future in as_completed(futures):
            try:
                records.extend(future.result())
            except Exception:  # noqa: BLE001 - one source failing must not sink the run
                continue
    return records