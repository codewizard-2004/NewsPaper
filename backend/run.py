"""Entry point for the Kernel Gazette daily pipeline.

Usage:
    uv run python run.py                 # full run: write today's issue to Firestore
    uv run python run.py --dry-run       # full graph, Publisher stubbed (no Firestore write)
    uv run python run.py --debug         # verbose per-node output
    uv run python run.py --smoke         # call the LLM once per task, then exit
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from rich.console import Console
from rich.panel import Panel

from agent import call_llm
from agent.core.config import TASKS, resolve_config
from agent.graph import build_graph, build_initial_state

console = Console()


def _banner(message: str, style: str = "blue") -> None:
    console.print(Panel(message, border_style=style))


def _smoke_test(force_model: str | None) -> None:
    """Call a real LLM for each task once, printing the resolved config + reply."""
    for task in TASKS:
        cfg = resolve_config(task, model=force_model)
        _banner(f"Smoke: task '{task}' -> provider={cfg.provider} model={cfg.model}", "cyan")
        try:
            result = call_llm(
                f"Reply in one short sentence. This is the '{task}' task.",
                task=task,
                model=force_model,
            )
            console.print(f"  -> {result}\n")
        except Exception as exc:  # noqa: BLE001
            console.print(f"  [red]ERROR[/red] {task}: {exc}\n")


def _run(stage: str, issue_date: str, debug: bool) -> dict:
    graph = build_graph()
    initial = build_initial_state(issue_date)
    _banner(f"Running pipeline: {stage} for {issue_date}", "blue")
    result = graph.invoke(initial)
    if debug:
        console.print("[dim]final state keys:[/dim]", list(result.keys()))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Kernel Gazette daily pipeline")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run research -> filter -> editor only (Phases 3-4); one edit LLM call, no journalist/publisher spend")
    parser.add_argument("--debug", action="store_true", help="Verbose per-node/per-task output")
    parser.add_argument("--smoke", action="store_true", help="Call the LLM once per task, then exit")
    parser.add_argument("--task", default=None, help="Override/force a specific model during --smoke")
    parser.add_argument("--date", default=None, help="Issue date (default: today)")
    args = parser.parse_args()

    if args.smoke:
        _smoke_test(args.task)
        return 0

    today = args.date or date.today().isoformat()

    # Phase 2: graph wires the linear spine + fan-out/in scaffolding with stubs.
    # Dry-run and full run currently behave the same (stubs); real divergence lands
    # in Phase 3 (research/filter) and Phase 6 (publisher staged to end).
    stage = "dry-run (research -> editor)" if args.dry_run else "full (writes issue)"
    result = _run(stage, today, args.debug)

    if args.debug:
        categorized = result.get("categorized") or {}
        for page, stories in categorized.items():
            console.print(f"  [cyan]{page}[/cyan]: {len(stories)} story(s)")
            for story in stories:
                console.print(f"    - {story.get('title')}")
        items = result.get("items") or []
        console.print(f"  [cyan]items[/cyan]: {len(items)} total")
        for it in items:
            kind = it.get("type")
            label = it.get("headline") or it.get("prompt") or it.get("caption") or ""
            console.print(f"    - [{kind}] {label[:70]}")

    categorized = result.get("categorized") or {}
    counts = ", ".join(f"{page}={len(stories)}" for page, stories in categorized.items()) or "none"

    items = result.get("items") or []
    article_count = sum(1 for it in items if it.get("type") == "article")
    dsa_count = sum(1 for it in items if it.get("type") == "dsa_question")
    comic_count = sum(1 for it in items if it.get("type") == "comic")
    errors = result.get("errors") or []

    issue = result.get("issue") or {}
    sections = issue.get("sections") or []
    section_counts = ", ".join(f"{s.get('name')}={len(s.get('items') or [])}" for s in sections) or "none"
    write_error = any(
        e.get("node") == "publisher" and e.get("story") == today for e in errors
    )
    published = "no (write skipped: no Firestore creds)" if write_error else "yes"

    _banner(
        f"[Phase 6] pipeline live: {len(result.get('raw_stories') or [])} raw, "
        f"{len(result.get('fresh_stories') or [])} fresh, categorized -> {counts}; "
        f"items: {article_count} articles, {dsa_count} DSA, {comic_count} comic; "
        f"issue: {len(sections)} section(s) [{section_counts}], published={published}"
        f"{f', {len(errors)} errors' if errors else ''}",
        "green",
    )
    if args.debug:
        for section in sections:
            console.print(f"  [cyan]section[/cyan] {section.get('name')}:")
            for item in section.get("items") or []:
                label = item.get("headline") or item.get("prompt") or item.get("caption") or "?"
                console.print(f"    - [{item.get('type')}] {str(label)[:70]}"
                              f"{' [img]' if item.get('image_url') else ''}")
        for err in errors:
            console.print(f"  [yellow]error[/yellow] {err.get('node')}: {err.get('story')} — {err.get('error')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())