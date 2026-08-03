"""Journalist nodes (Phase 5) — one per page bucket, run in parallel.

Each journalist writes full article text plus ``confidence_rating`` and
``importance_rating`` for its page's stories, emitting Firestore-shaped
``items`` that the ``operator.add`` reducer accumulates for the Publisher.

Search tool rule (cost control): a journalist calls ``search_web`` only when
``research_snippet_sufficient`` says the Research snippet is too thin to write
from. It never searches unconditionally.

The Misc journalist additionally owns the DSA rotation and the comic storyline
(via ``firebase/dsa.py`` + ``firebase/comic.py``). If Firestore is unreachable
(no credentials in dev), those extras degrade to skipping rather than failing
the issue.
"""

from __future__ import annotations

import logging
from typing import Callable

from agent.core.llm import call_llm_structured
from agent.graph.state import GazetteState
from agent.schema.issue import ComicScript
from agent.schema.story import ArticleDraft
from agent.tools.search_tool import search_web
from firebase.comic import get_comic_state, save_comic_state
from firebase.dsa import get_next_dsa_question, mark_dsa_used

log = logging.getLogger(__name__)

# Page buckets the Editor writes and journalists consume.
PAGES = ("front_page", "aiml_page", "security_page", "misc_page")

# Journalist node names, one per page bucket.
JOURNALIST_NODES = {page: f"journalist_{page}" for page in PAGES}

PAGE_LABELS = {
    "front_page": "Front page",
    "aiml_page": "AI/ML page",
    "security_page": "Security page",
    "misc_page": "Misc page",
}

# A Research snippet is "enough to write from" when it has at least this many
# words, or it is non-empty and two or more independent outlets cover the event.
SUFFICIENT_WORDS = 8

_JOURNALIST_SYSTEM = (
    'You are a staff journalist at "The Kernel Gazette", a single-person daily tech '
    "newspaper. You write clear, factual newspaper articles. Write ONLY from the "
    "research provided — never invent facts, quotes, people, or events. If a detail "
    "is unknown, say so plainly or omit it."
)

_COMIC_SYSTEM = (
    'You are the cartoonist for "The Kernel Gazette". You write the next installment '
    "of the ongoing tech-comic strip: witty, tech-savvy, continuing the established "
    "characters and arc, advancing the story one beat per day."
)


def research_snippet_sufficient(story: dict) -> bool:
    """True when the Research snippet alone is enough to write from.

    Concrete trigger: summary word count >= ``SUFFICIENT_WORDS``, OR the summary
    is non-empty and >= 2 independent outlets cover the event. Anything else is
    "insufficient" and may trigger the search fallback.
    """
    summary = (story.get("summary") or "").strip()
    if len(summary.split()) >= SUFFICIENT_WORDS:
        return True
    return bool(summary) and len(story.get("cluster_sources") or []) >= 2


def _clamp(value, low: float, high: float) -> float:
    """Coerce ``value`` into ``[low, high]``; unparseable values collapse to ``low``."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return low
    return max(low, min(high, value))


def _story_id(story: dict) -> str:
    url = story.get("url") or ""
    return url[-8:] or "x"


def _search_context(story: dict) -> str:
    """Enrich a too-thin snippet with a quick web search (fallback only)."""
    hits = search_web(story.get("title") or "")
    if not hits:
        return "none (search returned nothing)"
    return "\n".join(
        f"- {hit.get('title') or hit.get('url')} — {hit.get('snippet') or ''}"
        for hit in hits
    )


def _write_article(story: dict, page: str, date: str) -> tuple[dict | None, str | None]:
    """Write one article for ``story``.

    Returns ``(item, error)`` — on failure ``item`` is None and ``error`` is a
    short message (the article is skipped, never fatal).
    """
    title = story.get("title") or "(untitled)"
    sources = ", ".join(story.get("cluster_sources") or [story.get("source") or "?"])
    summary = (story.get("summary") or "").strip() or "No summary provided."
    url = story.get("url") or ""

    if research_snippet_sufficient(story):
        search_notes = "none (research snippet was sufficient)"
    else:
        search_notes = _search_context(story)

    prompt = (
        f"Write today's article for the {PAGE_LABELS[page]} page.\n\n"
        f"DATE: {date}\n"
        f"HEADLINE (keep as-is): {title}\n"
        f"URL: {url}\n"
        f"SOURCE(S): {sources}\n"
        f"RESEARCH SUMMARY:\n{summary}\n\n"
        f"SEARCH NOTES (additional context from a quick web check):\n{search_notes}\n\n"
        "Requirements:\n"
        "- 150-350 words, newspaper style; lead with the most important fact.\n"
        "- Stay strictly within the research and search notes above. No fabrication,\n"
        "  no speculation dressed as fact.\n"
        "- Return the article body and both ratings via the output schema.\n\n"
        "Ratings:\n"
        "- confidence_rating: 0.0 to 1.0 — how well-supported the article's facts are.\n"
        "- importance_rating: 0.0 to 10.0 — how significant this story is for today's paper."
    )

    try:
        draft = call_llm_structured(
            ArticleDraft, prompt, task="write", system=_JOURNALIST_SYSTEM
        )
    except Exception as exc:  # noqa: BLE001 - one article failing must not sink the page
        log.warning("journalist(%s): write failed for %r (%s); skipping", page, title[:60], exc)
        return None, str(exc)

    body = (getattr(draft, "body") or "").strip()
    if not body:
        return None, "LLM returned an empty article body"

    return (
        {
            "id": _story_id(story),
            "page": page,
            "type": "article",
            "headline": title,
            "body": body,
            "url": url,
            "sources": list(story.get("cluster_sources") or []),
            "confidence_rating": _clamp(draft.confidence_rating, 0.0, 1.0),
            "importance_rating": _clamp(draft.importance_rating, 0.0, 10.0),
            "image_url": None,
        },
        None,
    )


def _dsa_item() -> tuple[dict | None, str | None]:
    """Pull the next DSA question and mark it used; ``(None, reason)`` if unavailable."""
    try:
        question = get_next_dsa_question()
    except Exception as exc:  # noqa: BLE001 - Firestore may be unreachable in dev
        log.warning("Misc: DSA rotation unavailable (%s); skipping", exc)
        return None, str(exc)
    if not question:
        return None, "DSA bank exhausted (no unused questions)"

    qid = question.get("id") or ""
    if qid:
        try:
            mark_dsa_used(qid)
        except Exception as exc:  # noqa: BLE001 - already consumed for today's issue
            log.warning("Misc: could not mark DSA %s used (%s); continuing", qid, exc)

    return (
        {
            "id": qid or "dsa-?",
            "page": "misc_page",
            "type": "dsa_question",
            "prompt": question.get("prompt") or "",
            "difficulty": question.get("difficulty") or "medium",
        },
        None,
    )


def _comic_item() -> tuple[dict | None, str | None]:
    """Advance the comic storyline one beat; ``(None, reason)`` if state/write fails."""
    try:
        comic = get_comic_state()
    except Exception as exc:  # noqa: BLE001 - Firestore may be unreachable in dev
        log.warning("Misc: comic state unavailable (%s); skipping", exc)
        return None, str(exc)
    if not comic:
        return None, "no comic_state doc in Firestore"

    day = (comic.get("day_number") or 0) + 1
    prompt = (
        "Continue the strip.\n\n"
        f"ARC: {comic.get('arc_name') or '(untitled arc)'}\n"
        f"TODAY IS DAY: {day}\n"
        f"CHARACTERS: {', '.join(comic.get('characters') or [])}\n"
        f"LAST SYNOPSIS: {comic.get('last_synopsis') or '(series premiere)'}\n\n"
        "Write the next synopsis (1-3 sentences) and a short caption/tagline for "
        "today's panel. Stay in-character and on-arc; no reboot."
    )
    try:
        script = call_llm_structured(ComicScript, prompt, task="write", system=_COMIC_SYSTEM)
    except Exception as exc:  # noqa: BLE001 - comic write must not fail the issue
        log.warning("Misc: comic write failed (%s); skipping", exc)
        return None, str(exc)

    next_state = {
        "arc_name": comic.get("arc_name") or "(untitled arc)",
        "day_number": day,
        "last_synopsis": (getattr(script, "synopsis") or "").strip(),
        "characters": comic.get("characters") or [],
    }
    try:
        save_comic_state(next_state)
    except Exception as exc:  # noqa: BLE001 - state save is best-effort
        log.warning("Misc: could not save comic state (%s); continuing", exc)

    return (
        {
            "id": f"comic-{day:03d}",
            "page": "misc_page",
            "type": "comic",
            "image_url": None,
            "caption": (getattr(script, "caption") or getattr(script, "synopsis") or "").strip(),
        },
        None,
    )


def build_journalist(page: str) -> Callable[[GazetteState], dict]:
    """Return the journalist node body for ``page``.

    Writes full articles for the page's assigned stories; the Misc journalist
    additionally emits the daily DSA question and comic installment. Failed
    articles are skipped (logged into ``errors``, never fatal). Returns both
    ``items`` and ``errors`` (accumulated via their ``operator.add`` reducers).
    """

    def journalist_node(state: GazetteState) -> dict:
        categorized = state.get("categorized") or {}
        date = state.get("date") or ""
        items = []
        errors = []

        for story in categorized.get(page, []):
            item, error = _write_article(story, page, date)
            if item:
                items.append(item)
            elif error:
                errors.append(
                    {
                        "node": f"journalist_{page}",
                        "story": story.get("title") or "?",
                        "error": error,
                    }
                )

        if page == "misc_page":
            dsa, error = _dsa_item()
            if dsa:
                items.append(dsa)
            elif error:
                errors.append({"node": "journalist_misc_page", "story": "DSA", "error": error})

            comic, error = _comic_item()
            if comic:
                items.append(comic)
            elif error:
                errors.append({"node": "journalist_misc_page", "story": "comic", "error": error})

        return {"items": items, "errors": errors}

    return journalist_node
