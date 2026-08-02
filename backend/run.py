"""Entry point for the Kernel Gazette daily pipeline.

Usage:
    uv run python run.py                 # full run: write today's issue to Firestore
    uv run python run.py --dry-run       # research -> filter -> editor only (no writer/spend)
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
                        help="Run research -> filter -> editor only (Phases 3+); no LLM/image spend")
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

    _banner(
        f"[Phase 3] research+filter live: {len(result.get('raw_stories') or [])} raw, "
        f"{len(result.get('fresh_stories') or [])} fresh. "
        f"Editor/journalists/publisher are stubs until Phases 4-6. issue={result.get('issue')}",
        "green",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())