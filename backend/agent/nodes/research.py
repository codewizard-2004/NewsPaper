"""Research node.

Phase 3: pull stories from every source in parallel, then run ***same-day***
merge — cluster multiple sources covering one event into a single record with
``cluster_sources: [str]``. This is NOT cross-day dedup (that's Filter).

Deterministic, no LLM. Output: ``raw_stories: List[dict]``.
"""

from __future__ import annotations

import re

from agent.graph.state import GazetteState
from agent.tools.base import SourceRecord
from agent.tools.sources import fetch_all_sources


def _slug(title: str) -> str:
    """Lowercase, strip punctuation/stopwords, collapse spaces -> first 3 words."""
    words = re.sub(r"\W+", " ", title.lower()).split()
    stop = {"the", "a", "an", "for", "and", "with", "to", "of", "in", "on", "how", "why"}
    kept = [w for w in words if w not in stop]
    return " ".join(kept[:3])


def cluster_same_day(records: list[SourceRecord]) -> list[dict]:
    """Group same-event stories by title slug; keep highest-score lead per cluster."""
    buckets: dict[str, dict] = {}
    order: list[str] = []

    for rec in records:
        key = _slug(rec.title)
        if not key:
            continue
        if key not in buckets:
            buckets[key] = {
                "title": rec.title,
                "url": rec.url,
                "score": rec.score,
                "summary": rec.summary,
                "source": rec.source,
                "cluster_sources": [rec.source],
            }
            order.append(key)
        else:
            buckets[key]["cluster_sources"].append(rec.source)

    return [buckets[k] for k in order]


def research_node(state: GazetteState) -> dict:
    """Fetch all sources, cluster same-story records, populate ``raw_stories``."""
    records = fetch_all_sources()
    raw = cluster_same_day(records)
    return {"raw_stories": raw}