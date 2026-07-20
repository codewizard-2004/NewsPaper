import json
import os
import time
from datetime import date
from fastapi import APIRouter, HTTPException
from rich.console import Console
from rich.panel import Panel
from rich import box

from app.models.edition import EditionSchema
from app.graph.graph import newsroom_graph
from app.graph.models import set_global_callbacks
from app.graph.token_tracker import TokenCountingCallback, print_token_summary

console = Console()

router = APIRouter(
    prefix="/editions",
    tags=["editions"],
)

DESK_EMOJIS = {
    "Chief_Editor": "👔",
    "Front_Desk": "📰",
    "Economics_Desk": "📈",
    "AI_ML_Desk": "🤖",
    "Classifieds_Desk": "📋",
    "Weather_Puzzles_Desk": "🧩",
    "Obituaries_Births_Desk": "🪦",
    "Sports_Desk": "🏆",
    "Education_Desk": "🎓",
    "Security_Desk": "🔒",
    "Publish": "📰",
}


def _log_graph_event(event: dict) -> None:
    """Hook that prints every node transition as it happens."""
    if event.get("type") == "node":
        node = event.get("name", "")
        emoji = DESK_EMOJIS.get(node, "⚙️")
        # The event fires before the node runs, so LangGraph prints the rich output itself.
        # We just annotate the transition here with a subtle marker.
        if node:
            console.print(f"\n[dim]─── {emoji} Entering node: [bold]{node}[/bold] ───[/dim]")


@router.get("/latest", response_model=EditionSchema)
def get_latest_edition():
    """
    Returns the latest edition of the Daily Dispatch.
    For now, this mocks the database by reading the dummy.json file from the frontend.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        dummy_path = os.path.join(project_root, "frontend", "public", "dummy.json")
        with open(dummy_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load edition: {str(e)}")


@router.post("/generate")
def generate_edition():
    """
    Triggers the LangGraph multi-agent newsroom to generate a new edition.
    """
    today = date.today().isoformat()

    # ── Splash banner ───────────────────────────────────────────────────────
    console.print()
    console.print(Panel(
        "[bold yellow]📰  THE DAILY DISPATCH — NEWSROOM PIPELINE[/bold yellow]\n\n"
        f"[dim]Launching multi-agent newsroom for[/dim] [bold]{today}[/bold]\n"
        "[dim]Supervisor: Chief Editor[/dim]  ·  "
        "[dim]9 specialist desks[/dim]  ·  "
        "[dim]LangGraph orchestration[/dim]",
        border_style="bright_yellow",
        box=box.HEAVY,
        subtitle="🚀 Starting generation",
    ))

    start_time = time.time()
    token_tracker = TokenCountingCallback()
    set_global_callbacks([token_tracker])

    try:
        # ── Use invoke() directly (avoids double-run bug with stream) ────────
        initial_state = {
            "date": today,
            "settings": {},
            "assignments": [],
            "drafts": [],
            "messages": [],
            "errors": [],
            "compiled_edition": None,
        }

        final_state = newsroom_graph.invoke(
            initial_state,
            {"recursion_limit": 50},
        )

        elapsed = time.time() - start_time
        compiled = final_state.get("compiled_edition")

        print_token_summary([token_tracker])

        if compiled:
            console.print()
            console.print(Panel(
                f"[bold green]✅  EDITION COMPLETE[/bold green]\n\n"
                f"[green]Pages:[/green] {len(compiled.get('pages', []))}\n"
                f"[green]Articles:[/green] {sum(len(p.get('articles', [])) for p in compiled.get('pages', []))}\n"
                f"[green]Date:[/green] {compiled.get('issueDate', today)}\n"
                f"[dim]Completed in {elapsed:.1f}s[/dim]",
                border_style="green",
                box=box.HEAVY,
                subtitle="🏁 Pipeline finished",
            ))
            return compiled

        drafts = final_state.get("drafts", [])
        approved = [d for d in drafts if d.status == "approved"]
        rejected = [d for d in drafts if d.status == "rejected"]
        console.print(f"[yellow]⚠️  Pipeline finished in {elapsed:.1f}s with {len(approved)} approved, {len(rejected)} rejected, {len(drafts)} total drafts but no edition.[/yellow]")
        for d in drafts:
            console.print(f"  [{'green' if d.status=='approved' else 'red' if d.status=='rejected' else 'yellow'}]{d.section}[{d.article_index}]: {d.headline[:60]} -> {d.status}[/]")
        return {
            "status": "partial",
            "message": f"Graph completed with {len(approved)} approved drafts but no edition was compiled.",
            "drafts_count": len(approved),
            "errors": final_state.get("errors", []),
        }
    except Exception as e:
        elapsed = time.time() - start_time
        console.print(f"[bold red]💥 Pipeline failed after {elapsed:.1f}s: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
