"""Shared plumbing for source tools.

Defines the normalized story shape every source emits and a small HTTP
helper so each source module stays terse and consistent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

USER_AGENT = "KernelGazette/1.0"


@dataclass(frozen=True)
class SourceRecord:
    """Normalized story from any feed.

    ``score`` is source-specific (HN/Reddit/GitHub points, Dev.to reactions) or 0
    for RSS feeds that carry none. ``summary`` may be a short snippet.
    """

    source: str
    title: str
    url: str
    score: float = 0.0
    summary: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "score": self.score,
            "summary": self.summary,
        }


def http_get(url: str, *, timeout: float = 15.0) -> bytes:
    """Fetch ``url`` and return raw bytes, raising on transport/HTTP errors."""
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as response:  # noqa: S310 - expected public fetches
        return response.read()


def http_get_json(url: str, **kwargs) -> dict:
    """Fetch ``url`` and decode as JSON."""
    return json.loads(http_get(url, **kwargs).decode("utf-8"))


def http_get_text(url: str, **kwargs) -> str:
    """Fetch ``url`` and return decoded UTF-8 text."""
    return http_get(url, **kwargs).decode("utf-8")


def make_records(source: str, items: list[dict]) -> list[SourceRecord]:
    """Build SourceRecords, dropping any entry without a usable URL."""
    records = []
    for item in items:
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        if not url or not title:
            continue
        records.append(
            SourceRecord(
                source=source,
                title=title,
                url=url,
                score=float(item.get("score") or 0.0),
                summary=(item.get("summary") or "").strip(),
            )
        )
    return records