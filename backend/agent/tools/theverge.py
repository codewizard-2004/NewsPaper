"""The Verge RSS source."""

from __future__ import annotations

import re

import feedparser

from agent.tools.base import SourceRecord


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch_the_verge(limit: int = 5) -> list[SourceRecord]:
    """Latest The Verge articles via RSS."""
    feed = feedparser.parse("https://www.theverge.com/rss/index.xml")

    records = []
    for entry in feed.entries[:limit]:
        url = (entry.get("link") or "").strip()
        title = (entry.get("title") or "").strip()
        if not url or not title:
            continue
        records.append(
            SourceRecord(
                source="The Verge",
                title=title,
                url=url,
                score=0.0,
                summary=_clean_html(entry.get("summary", ""))[:280],
            )
        )
    return records