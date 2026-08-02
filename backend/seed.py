"""Seed the Kernel Gazette Firestore collections from ``backend/fixtures/``.

Phase 2 deliverable: make `seen_stories`, `dsa_bank`, `comic_state`, and
`issues/{date}` exist with starter data so the frontend can swap from mock to
real before the live pipeline (Phases 3-6) is finished.

Ownership per ``agents.md``: seeding is a one-off setup tool, NOT a graph node.

Usage:
    uv run python seed.py                     # write all fixtures to Firestore
    uv run python seed.py --date 2026-08-02   # uses issues/{date} with that date
    uv run python seed.py --dry-run           # print the plan, touch no network
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()
FIXTURES = Path(__file__).parent / "fixtures"

COMIC_DOC = "current"


def _load(name: str):
    with open(FIXTURES / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _print_plan(rows: list[tuple[str, str, str]]) -> None:
    table = Table(title="Seed plan")
    for col in ("Collection", "Doc / ID", "Action"):
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def _run(issue_date: str, dry_run: bool) -> int:
    dsa = _load("dsa_bank.json")
    comic = _load("comic_state.json")
    issue = _load("issue.json")
    issue["date"] = issue_date

    action = "write" if not dry_run else "dry-run"

    rows: list[tuple[str, str, str]] = []
    for q in dsa:
        rows.append(("dsa_bank", q["id"], action))
    rows.append(("comic_state", COMIC_DOC, action))
    rows.append(("issues", issue_date, action))

    _print_plan(rows)

    if dry_run:
        console.print("[yellow]dry-run: not writing to Firestore.[/yellow]")
        return 0

    from firebase.firebase import db

    for q in dsa:
        doc = {
            "prompt": q["prompt"],
            "difficulty": q["difficulty"],
            "used": False,
        }
        db().collection("dsa_bank").document(q["id"]).set(doc)
    db().collection("comic_state").document(COMIC_DOC).set(comic)
    db().collection("issues").document(issue_date).set(issue)

    console.print("[green]Seeded Firestore from fixtures.[/green]")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Gazette Firestore collections")
    parser.add_argument("--date", default=None, help="issues/{date} to write (default today)")
    parser.add_argument("--dry-run", action="store_true", help="Validate + plan, no network")
    args = parser.parse_args()
    issue_date = args.date or date.today().isoformat()
    return _run(issue_date, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())