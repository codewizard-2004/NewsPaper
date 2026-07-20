import json
import re
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from app.graph.state import NewsroomState
from app.graph.schema.models import Assignment, DraftReview, DraftArticle
from app.graph.schema.system_prompt import CHIEF_EDITOR_PROMPT
from app.graph.models import get_llm

console = Console()


def _draft_status_tag(d: DraftArticle) -> str:
    m = {"approved": "[green]✅ Approved[/green]", "rejected": "[red]❌ Rejected[/red]", "draft": "[yellow]⏳ Draft[/yellow]"}
    return m.get(d.status, d.status)


def _parse_decision(raw: str) -> Optional[dict]:
    """Parse the LLM's raw text response into a decision dict.
    Tries JSON extraction first, then falls back to regex extraction."""
    # Try to find JSON in code blocks or standalone
    for pattern in [r"```(?:json)?\s*\n?(.*?)```", r"(\{.*\})", r"(\[.*\])"]:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                continue

    # Fallback: extract assignments and reviews from markdown-like table
    result = {"assignments": [], "reviews": [], "all_drafts_approved": False}
    lines = raw.strip().split("\n")
    for line in lines:
        line = line.strip()
        # Match table rows like "| front_desk | topic ... |"
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 2:
                desk = cells[0].strip("*").strip("**").strip()
                topic = cells[1].strip("*").strip("**").strip()
                if desk and topic and len(topic) > 10:
                    result["assignments"].append({"desk": desk, "topic": topic})

    if not result["assignments"]:
        return None

    result["all_drafts_approved"] = True
    return result


def _build_json_prompt(context: str) -> str:
    """Build a prompt that explicitly requests JSON output."""
    return f"""{context}

IMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no backticks, no explanation.

The JSON schema is:
{{
  "assignments": [
    {{"desk": "desk_name", "topic": "detailed assignment topic"}}
  ],
  "reviews": [
    {{"section": "desk_name", "headline": "exact headline of the article being reviewed", "approved": true, "feedback": null, "importance": 3}}
  ],
  "all_drafts_approved": false
}}

If creating initial assignments, set "reviews" to [] and "all_drafts_approved" to false.
If reviewing drafts, set "assignments" to [] unless you need to create new ones.
For each draft, include a review: approved=true with 1-5 importance, or approved=false with feedback.
IMPORTANT: When a desk has contributed multiple articles, review EACH article individually by including its exact headline in the review. This lets you approve some and reject others.

Valid desk names: front_desk, economics_desk, ai_ml_desk, classifieds_desk, weather_puzzles_desk, obituaries_births_desk, sports_desk, education_desk, security_desk

Respond with ONLY the JSON object, nothing else."""


def chief_editor_node(state: NewsroomState) -> Dict[str, Any]:
    console.print()
    console.print(
        Panel(
            "[bold green]👔  CHIEF EDITOR — Morning Standup[/bold green]\n"
            f"[dim]Date: {state.get('date', 'Unknown')}[/dim]",
            border_style="green",
            subtitle="📰 The Daily Dispatch",
        )
    )

    assignments = state.get("assignments", [])
    drafts = state.get("drafts", [])

    llm = get_llm("chief_editor")
    context_lines = [f"Current Date: {state.get('date', 'Unknown')}\n"]

    if drafts:
        review_table = Table(
            title=f"📋 Drafts Pending Review ({len(drafts)} total)",
            box=box.ROUNDED,
            border_style="yellow",
        )
        review_table.add_column("#", style="dim", width=3)
        review_table.add_column("Section", style="cyan")
        review_table.add_column("Status", width=16)
        review_table.add_column("Headline", style="bold", max_width=50)
        review_table.add_column("Paras")
        review_table.add_column("Tags")
        for i, d in enumerate(drafts):
            tags = ", ".join(d.tags[:3]) if d.tags else "[dim]—[/dim]"
            paras = str(len(d.body_paragraphs)) if d.body_paragraphs else "0"
            review_table.add_row(str(i), d.section, _draft_status_tag(d), d.headline[:48], paras, tags)
        console.print(review_table)

        context_lines.append("Submitted Drafts to Review:\n")
        for i, d in enumerate(drafts):
            context_lines.append(
                f"[{i}] Desk: {d.section} | Index: {d.article_index} | Status: {d.status}\n"
                f"  Headline: {d.headline}\n  Dek: {d.dek}\n  Summary: {d.summary[:300]}\n"
            )
    else:
        console.print(Panel(
            "[yellow]📭 No drafts have been submitted yet.[/yellow]\n\n"
            "The Chief Editor must create assignments for 3-5 desks to begin the pipeline.",
            border_style="yellow", title="📭 No Drafts Yet",
        ))
        context_lines.append(
            "No drafts submitted yet. Create broad assignments for these key desks:\n"
            "front_desk, economics_desk, ai_ml_desk, education_desk, security_desk\n"
            "Each desk will produce 6 articles on its assigned topic, so pick broad topics with 6+ angles.\n"
            "Desks: front_desk, economics_desk, ai_ml_desk, classifieds_desk, "
            "weather_puzzles_desk, obituaries_births_desk, sports_desk, education_desk, security_desk"
        )

    prompt = _build_json_prompt("\n".join(context_lines))
    console.print(Panel(
        f"[dim]Sending to LLM...[/dim]\n[italic]{prompt[:500]}[/italic]",
        border_style="dim", title="🧠 Chief Editor's Context (preview)",
    ))

    console.print(Panel(
        "[bold yellow]🤔 Chief Editor is evaluating and drafting decisions...[/bold yellow]",
        border_style="yellow", title="Thinking",
    ))

    messages = [
        SystemMessage(content=CHIEF_EDITOR_PROMPT),
        HumanMessage(content=prompt),
    ]

    try:
        raw = llm.invoke(messages).content.strip()
        console.print(Panel(
            f"[dim]Raw LLM response (first 600 chars):[/dim]\n{raw[:600]}",
            border_style="dim", title="📨 LLM Response",
        ))

        parsed = _parse_decision(raw)
        if parsed is None:
            raise ValueError("Could not parse LLM output as structured decision")

        assignments = [Assignment(**a) for a in parsed.get("assignments", [])]
        reviews = [DraftReview(**r) for r in parsed.get("reviews", [])]
        all_approved = parsed.get("all_drafts_approved", False)

        # ── Render decisions ─────────────────────────────────────────────────
        decision_table = Table(title="📰 Chief Editor's Decisions", box=box.ROUNDED, border_style="green")
        decision_table.add_column("Type", style="bold", width=12)
        decision_table.add_column("Details", style="white")
        for a in assignments:
            decision_table.add_row("[cyan]📌 Assignment[/cyan]", f"[cyan]{a.desk}[/cyan]: {a.topic}")
        for r in reviews:
            if r.approved:
                imp = f" (importance: {r.importance})" if r.importance else ""
                decision_table.add_row("[green]✅ Approved[/green]", f"[green]{r.section}[/green]{imp}")
            else:
                fb = f"\n    [red]Feedback: {r.feedback}[/red]" if r.feedback else ""
                decision_table.add_row("[red]❌ Rejected[/red]", f"[red]{r.section}[/red]{fb}")
        if all_approved:
            decision_table.add_row("[bold green]🏁 COMPLETE[/bold green]", "[bold green]All drafts approved![/bold green]")
        console.print(decision_table)

        # ── Apply reviews ────────────────────────────────────────────────────
        updated_drafts: list[DraftArticle] = []
        for draft in drafts:
            def headline_match(r: DraftReview) -> bool:
                if r.headline:
                    return r.section == draft.section and r.headline == draft.headline
                return r.section == draft.section
            review = next((r for r in reviews if headline_match(r)), None)
            if review:
                if review.approved:
                    draft.status = "approved"
                    if review.importance is not None:
                        draft.importance = review.importance
                else:
                    draft.status = "rejected"
                    draft.feedback = review.feedback
            else:
                # If a desk-level review exists without a headline, apply it to all articles from that desk
                desk_review = next((r for r in reviews if r.section == draft.section and not r.headline), None)
                if desk_review:
                    if desk_review.approved:
                        draft.status = "approved"
                        if desk_review.importance is not None:
                            draft.importance = desk_review.importance
            updated_drafts.append(draft)

        existing_assignments = state.get("assignments", [])
        if drafts:
            final_assignments = existing_assignments if existing_assignments else [a.dict() for a in assignments]
        else:
            final_assignments = [a.dict() for a in assignments]

        if updated_drafts:
            approved_count = sum(1 for d in updated_drafts if d.status == "approved")
            rejected_count = sum(1 for d in updated_drafts if d.status == "rejected")
            console.print(Panel(
                f"[bold]Summary:[/bold] {len(updated_drafts)} drafts — "
                f"[green]{approved_count} approved[/green], "
                f"[red]{rejected_count} rejected[/red], "
                f"[bold]{len(final_assignments)} assignment(s)[/bold]",
                border_style="green",
            ))

        result: Dict[str, Any] = {"assignments": final_assignments}
        if updated_drafts:
            result["drafts"] = updated_drafts

        # Reset completed_desks accumulator for the next dispatch cycle.
        result["completed_desks"] = []

        return result

    except Exception as e:
        console.print(Panel(
            f"[bold red]💥 Chief Editor Error: {str(e)}[/bold red]",
            border_style="red", title="Error",
        ))
        return {}
