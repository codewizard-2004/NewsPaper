"""``seen_stories`` collection — Filter node reads, Publisher writes."""

from __future__ import annotations

from datetime import datetime, timezone

from firebase.firebase import db, story_hash


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def get_seen(url: str) -> bool:
    """Return True if a story with this canonical URL was already published."""
    snap = db().collection("seen_stories").document(story_hash(url)).get()
    return snap.exists


def mark_published(url: str, date: str | None = None) -> None:
    """Record a published story in ``seen_stories`` (Publisher node only)."""
    db().collection("seen_stories").document(story_hash(url)).set(
        {"url": url, "published_date": date or _today_utc()}
    )