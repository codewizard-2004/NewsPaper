"""Image search tool — Publisher only (Phase 6).

Called only for articles above the importance threshold (see ``publisher.py``)
so image fetching stays a cost-controlled exception, not a default. Wraps
DuckDuckGo's image search; results are normalized to
``{image_url, source_url, title}``. Any failure returns ``[]`` — an article
keeps ``image_url=None`` rather than sinking the issue.
"""

from __future__ import annotations

import logging

from ddgs import DDGS

log = logging.getLogger(__name__)


def search_images(query: str, max_results: int = 4) -> list[dict]:
    """Search for an image for ``query`` and return normalized results; ``[]`` on failure."""
    try:
        with DDGS() as ddgs:
            raw = ddgs.images(query, max_results=max_results)
    except Exception as exc:  # noqa: BLE001 - a failed image search must not sink the run
        log.warning("search_images failed for %r (%s); article keeps no image", query[:60], exc)
        return []

    results: list[dict] = []
    for item in raw:
        image_url = (item.get("image") or "").strip()
        if not image_url:
            continue
        results.append(
            {
                "image_url": image_url,
                "source_url": (item.get("url") or "").strip(),
                "title": (item.get("title") or "").strip(),
            }
        )
    return results
