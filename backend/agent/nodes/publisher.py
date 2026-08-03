"""Publisher node (Phase 6).

    items --(confidence filter, fold thin pages, images)--> issue -> Firestore.

The only node allowed to *write* to Firestore and the only one allowed to call
the image search tool. Responsibilities, in order:

1. Confidence filter — drop articles below ``PUBLISHER_CONFIDENCE_THRESHOLD``
   (DSA/comic items always pass; they carry no rating).
2. Thin-page fold — any page with fewer than ``PUBLISHER_MIN_PAGE_ITEMS`` items
   folds into Misc. This is the ONLY place page structure changes; journalists
   never reassign pages.
3. Images — fetch one only for articles above ``PUBLISHER_IMAGE_IMPORTANCE``.
4. Compose ``issues/{date}`` = ``{date, sections: [{name, items}]}`` and write it,
   then mark every published story in ``seen_stories``.

Degradation: if Firestore is unreachable (no credentials in dev), the issue is
still composed into ``state.issue`` and the failure is logged (never fatal) —
mirroring Filter's keep-all degrade.
"""

from __future__ import annotations

import logging

from agent.core.config import (
    PUBLISHER_CONFIDENCE_THRESHOLD,
    PUBLISHER_IMAGE_IMPORTANCE,
    PUBLISHER_MIN_PAGE_ITEMS,
)
from agent.graph.state import GazetteState
from agent.tools.image_search_tool import search_images
from firebase.issues import read_issue, write_issue
from firebase.seen import mark_published

log = logging.getLogger(__name__)

# Page buckets (mirrors journalist.PAGES) + their public section names.
PAGES = ("front_page", "aiml_page", "security_page", "misc_page")
SECTION_NAMES = {
    "front_page": "Front page",
    "aiml_page": "AI/ML",
    "security_page": "Security",
    "misc_page": "Misc",
}

# Internal item fields stripped before writing to Firestore (grouping/lookups only).
_INTERNAL_FIELDS = ("page", "url")


def _group_by_page(items: list[dict]) -> dict[str, list[dict]]:
    pages = {page: [] for page in PAGES}
    for item in items:
        pages.setdefault(item.get("page") or "misc_page", []).append(item)
    return pages


def _confidence_filter(pages: dict[str, list[dict]]) -> None:
    """Drop articles below the confidence threshold (in place)."""
    for page in pages:
        pages[page] = [
            item
            for item in pages[page]
            if item.get("type") != "article"
            or float(item.get("confidence_rating") or 0.0) >= PUBLISHER_CONFIDENCE_THRESHOLD
        ]


def _fold_thin_pages(pages: dict[str, list[dict]]) -> list[str]:
    """Fold sub-minimum pages into Misc; return the folded page names."""
    folded = []
    for page in PAGES:
        if page == "misc_page":
            continue
        if len(pages[page]) < PUBLISHER_MIN_PAGE_ITEMS:
            pages["misc_page"].extend(pages[page])
            pages[page] = []
            folded.append(page)
    return folded


def _attach_images(pages: dict[str, list[dict]]) -> int:
    """Fetch an image for articles above the importance threshold; return count fetched."""
    fetched = 0
    for page in pages:
        for item in pages[page]:
            if item.get("type") != "article":
                continue
            if float(item.get("importance_rating") or 0.0) < PUBLISHER_IMAGE_IMPORTANCE:
                continue
            hits = search_images(item.get("headline") or "")
            if hits:
                item["image_url"] = hits[0]["image_url"]
                fetched += 1
    return fetched


def _compose_sections(pages: dict[str, list[dict]]) -> list[dict]:
    sections = []
    for page in PAGES:
        items = pages[page]
        if not items:
            continue
        clean = []
        for item in items:
            clean.append({k: v for k, v in item.items() if k not in _INTERNAL_FIELDS})
        sections.append({"name": SECTION_NAMES[page], "items": clean})
    return sections


def _already_published(date: str) -> bool:
    """True if an issue for ``date`` already exists (idempotency guard).

    Re-running an already-published date must not duplicate or clobber the
    issue. A failed lookup degrades to False (assume not published) so an
    offline/unreachable Firestore never blocks a first write.
    """
    try:
        return read_issue(date) is not None
    except Exception:  # noqa: BLE001 - a lookup failure must not block publishing
        return False


def _publish(date: str, issue: dict, items: list[dict], errors: list[dict]) -> None:
    """Write the issue, then mark every published story seen. Failures are logged, never fatal."""
    try:
        if _already_published(date):
            log.info("Publisher: %s already published; skipping (idempotent re-run)", date)
            return
        write_issue(date, issue)
    except Exception as exc:  # noqa: BLE001 - dev runs have no Firestore credentials
        log.warning("Publisher: write_issue failed (%s); issue composed but not persisted", exc)
        errors.append({"node": "publisher", "story": date, "error": str(exc)})
        return

    marked = 0
    for item in items:
        if item.get("type") != "article":
            continue
        url = (item.get("url") or "").strip()
        if not url:
            continue
        try:
            mark_published(url, date)
            marked += 1
        except Exception as exc:  # noqa: BLE001 - a seen-mark failure must not undo the issue
            log.warning("Publisher: mark_published failed for %r (%s); continuing", url[:60], exc)
            errors.append({"node": "publisher", "story": url, "error": str(exc)})
    log.info("Publisher: wrote %s and marked %s stories seen", date, marked)


def publisher_node(state: GazetteState) -> dict:
    """Assemble and write today's issue; return the composed issue + any errors."""
    date = state.get("date") or ""
    items = state.get("items") or []
    errors: list[dict] = []

    pages = _group_by_page(items)
    _confidence_filter(pages)
    folded = _fold_thin_pages(pages)
    images_fetched = _attach_images(pages)
    sections = _compose_sections(pages)
    issue = {"date": date, "sections": sections}

    log.info(
        "Publisher: %d items -> %d sections (folded=%s, images=%d)",
        len(items), len(sections), folded, images_fetched,
    )

    _publish(date, issue, items, errors)
    return {"issue": issue, "errors": errors}
