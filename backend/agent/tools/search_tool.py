"""Search tool — journalist fallback only (Phase 5).

Called *only* when a Research snippet is too thin to write from (see
``agent.nodes.journalist.research_snippet_sufficient``). Never called
unconditionally — cost control as much as quality control.

DuckDuckGo is the backend (free, keyless). Results are normalized to
``{title, url, snippet}``. Any failure returns ``[]`` so a search outage never
sinks the day's run — the journalist just writes from what it has.
"""

from __future__ import annotations

import logging

from ddgs import DDGS

log = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 4) -> list[dict]:
    """Web-search ``query`` and return normalized results; ``[]`` on any failure."""
    try:
        with DDGS() as ddgs:
            raw = ddgs.text(query, max_results=max_results)
    except Exception as exc:  # noqa: BLE001 - a failed search must not sink the run
        log.warning("search_web failed for %r (%s); continuing without it", query[:60], exc)
        return []

    results: list[dict] = []
    for item in raw:
        url = (item.get("href") or "").strip()
        if not url:
            continue
        results.append(
            {
                "title": (item.get("title") or "").strip(),
                "url": url,
                "snippet": (item.get("body") or "").strip(),
            }
        )
    return results
