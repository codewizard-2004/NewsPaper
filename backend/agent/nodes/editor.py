"""Editor node (Phase 4).

    fresh_stories -> (one structured LLM call, task "edit") -> categorized {page => [stories]}

The Editor is the only node with editorial judgment: it picks a **target range
per page** (3-10, never a fixed count) and buckets stories into ``front_page``,
``aiml_page``, ``security_page``, ``misc_page``. Thin days stay thin — a page
that earns nothing is simply absent from the output.

No-invention enforcement: the LLM answers with *indices* into ``fresh_stories``
(:class:`EditorSelection`). We map indices back to the real story dicts and drop
anything out of range, so the model structurally cannot fabricate a story.

If the model/provider fails (or structured output won't parse), we degrade to a
deterministic keyword bucket so a provider outage never kills the day's issue —
mirroring Filter's keep-all degrade.
"""

from __future__ import annotations

import logging

from agent.core.llm import call_llm_structured
from agent.graph.state import GazetteState
from agent.schema.story import EditorSelection

log = logging.getLogger(__name__)

# Same page buckets as ``journalist.PAGES``; duplicated here (not imported from
# nodes) to keep nodes independent of each other.
PAGES = ("front_page", "aiml_page", "security_page", "misc_page")

PAGE_BLURBS = {
    "front_page": "the day's most important, can't-miss stories",
    "aiml_page": "AI and machine learning",
    "security_page": "security, privacy, vulnerabilities, breaches",
    "misc_page": "everything else worth printing (dev tools, languages, hardware, science, opinion)",
}

TARGET = "3 to 10"

_SYSTEM = (
    "You are the Editor of \"The Kernel Gazette\", a single-person daily tech newspaper. "
    "Your job is page assignment only: decide which wire stories run, and on which page. "
    "You do not write articles and you do not invent stories."
)

_AI_KEYWORDS = (
    "ai", "artificial intelligence", "machine learning", "llm", "large language model",
    "gpt", "gemini", "claude", "openai", "anthropic", "deepmind", "transformer",
    "neural", "diffusion", "copilot", "model", "agent",
)
_SECURITY_KEYWORDS = (
    "security", "vulnerability", "exploit", "cve", "hack", "hacker", "breach",
    "malware", "ransomware", "phishing", "zero-day", "encryption", "privacy",
    "ddos", "firewall", "authentication", "backdoor", "leak",
)


def _build_catalog(fresh_stories: list[dict]) -> str:
    """Render fresh stories as a numbered catalog for the model to pick from."""
    lines = []
    for idx, story in enumerate(fresh_stories):
        sources = ", ".join(story.get("cluster_sources") or [])
        summary = (story.get("summary") or "").strip().replace("\n", " ")[:220]
        lines.append(
            f"[{idx}] {story.get('title') or '(untitled)'}\n"
            f"    source(s): {sources or story.get('source') or '?'} | score={story.get('score', 0)}\n"
            f"    {summary}"
        )
    return "\n".join(lines)


def _build_prompt(date: str, catalog: str) -> str:
    pages = "\n".join(
        f"- {page} ({TARGET}): {PAGE_BLURBS[page]}" for page in PAGES
    )
    return (
        f"Today is {date}. Below is the numbered catalog of fresh stories from the "
        "wires (index in brackets). Assign the day's running order.\n\n"
        f"Pages and target ranges (aim for these, but NEVER pad to fill them — "
        "if the day is thin a page may get fewer, or none):\n"
        f"{pages}\n\n"
        "Rules:\n"
        "1. Assign only indices that exist in the catalog — never invent, rename, or merge stories.\n"
        "2. Assign each index to at most one page.\n"
        "3. Prefer higher-signal stories: multiple sources covering one event (cluster_sources), higher score.\n"
        "4. Fit over quota: quality beats hitting the range.\n"
        "5. Leaving stories unassigned is fine; they simply don't print today.\n\n"
        f"Catalog:\n{catalog}"
    )


def _selection_to_categorized(fresh_stories: list[dict], selection: EditorSelection) -> dict[str, list[dict]]:
    """Map the model's index picks back to real story dicts, dropping anything invalid."""
    assigned: set[int] = set()
    categorized: dict[str, list[dict]] = {}

    for page in PAGES:
        indices = getattr(selection, page) or []
        for idx in indices:
            if not isinstance(idx, int) or idx < 0 or idx >= len(fresh_stories):
                continue  # model tried to assign a story that doesn't exist
            if idx in assigned:
                continue  # same story on two pages: keep the first assignment
            assigned.add(idx)
            story = dict(fresh_stories[idx])
            story["page"] = page
            categorized.setdefault(page, []).append(story)

    return categorized


def _fallback_categorize(fresh_stories: list[dict]) -> dict[str, list[dict]]:
    """Deterministic bucket used when the edit call fails. Never invents stories.

    Keyword matches feed the AI/ML and Security pages; the remaining stories are
    ranked by score, top ~10 to the front page and the overflow to Misc.
    """
    categorized: dict[str, list[dict]] = {}
    used: set[int] = set()

    for idx, story in enumerate(fresh_stories):
        text = f"{story.get('title')} {story.get('summary')}".lower()
        page = None
        if any(kw in text for kw in _AI_KEYWORDS):
            page = "aiml_page"
        elif any(kw in text for kw in _SECURITY_KEYWORDS):
            page = "security_page"
        if page is not None:
            categorized.setdefault(page, []).append(dict(fresh_stories[idx]))
            used.add(idx)

    leftovers = [dict(story) for idx, story in enumerate(fresh_stories) if idx not in used]
    leftovers.sort(key=lambda story: story.get("score", 0.0), reverse=True)

    if leftovers:
        categorized["front_page"] = leftovers[:10]
        if len(leftovers) > 10:
            categorized.setdefault("misc_page", []).extend(leftovers[10:])

    for page, stories in categorized.items():
        for story in stories:
            story["page"] = page
    return categorized


def editor_node(state: GazetteState) -> dict:
    """Select a target range per page and categorize ``fresh_stories``."""
    fresh = state.get("fresh_stories") or []
    if not fresh:
        return {"categorized": {}}

    catalog = _build_catalog(fresh)
    try:
        selection = call_llm_structured(
            EditorSelection,
            _build_prompt(state.get("date", ""), catalog),
            task="edit",
            system=_SYSTEM,
        )
        categorized = _selection_to_categorized(fresh, selection)
        log.info("Editor: LLM assignment used (%s stories selected)", sum(len(v) for v in categorized.values()))
    except Exception as exc:  # noqa: BLE001 - provider outage must not kill the issue
        log.warning("Editor LLM call failed (%s); using deterministic fallback", exc)
        categorized = _fallback_categorize(fresh)

    return {"categorized": categorized}
