from typing import Dict, Any, Callable, Optional
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import json
import re

from app.graph.state import NewsroomState
from app.graph.schema.models import DraftArticle, ArticleImage, SourceAttribution
from app.graph.models import get_llm

console = Console()

ARTICLES_PER_BATCH = 6


def _summarise_tool_result(tool_name: str, raw: str) -> str:
    """Condense a tool result into a short summary line."""
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return f"→ returned {len(data)} items"
        if isinstance(data, dict):
            if "error" in data:
                return f"❌ ERROR: {data['error'][:80]}"
            keys = list(data.keys())
            return f"→ dict with keys: {', '.join(keys[:4])}"
    except (json.JSONDecodeError, TypeError):
        pass
    length = len(raw)
    preview = raw[:120].replace("\n", " ")
    return f"→ {length} chars: \"{preview}...\"" if length > 120 else f"→ \"{preview}\""


def _parse_article_json(text: str) -> dict | list:
    """Extract and parse JSON from LLM text output, with fallbacks.
    Returns a dict (single article) or list (multiple articles), or empty dict on failure."""
    if not text:
        return {}
    text = text.strip()

    # Try parsing the whole thing as JSON first (handles bare JSON with no markdown)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code blocks
    for pattern in [r'```(?:json)?\s*\n?(.*?)```', r'(\[.*?\])', r'(\{.*\})']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
                if isinstance(parsed, (dict, list)):
                    return parsed
            except (json.JSONDecodeError, IndexError):
                continue

    return {}


def _render_tool_args(args: dict) -> str:
    """Pretty-print tool arguments for terminal display."""
    parts = []
    for k, v in args.items():
        if isinstance(v, str) and len(v) > 60:
            v = v[:60] + "..."
        parts.append(f"{k}={v}")
    return ", ".join(parts) if parts else "(no args)"


def create_desk_node(desk_name: str, byline: str, system_prompt: str, tools: list = []) -> Callable:
    """
    Factory function to create a LangGraph node for a specific journalist desk.
    """
    display_name = desk_name.replace("_", " ").title()

    def desk_node(state: NewsroomState) -> Dict[str, Any]:

        assignments = state.get("assignments", [])
        my_assignment = next((a for a in assignments if a.get("desk") == desk_name), None)

        drafts = state.get("drafts", [])
        my_drafts = [d for d in drafts if d.section == desk_name]
        all_approved = my_drafts and all(d.status == "approved" for d in my_drafts)
        any_rejected = any(d.status == "rejected" for d in my_drafts)
        rejected_feedback = [d.feedback for d in my_drafts if d.status == "rejected" and d.feedback]

        # ── Header ──────────────────────────────────────────────────────────
        header = Table.grid(padding=(0, 1))
        header.add_column(style="bold cyan", justify="right")
        header.add_column(style="white")
        header.add_row("SECTION", f"[bold cyan]{display_name}[/bold cyan]")
        header.add_row("MODEL", byline)
        if my_assignment:
            header.add_row("TOPIC", f"[italic]{my_assignment['topic']}[/italic]")
        article_count = len(my_drafts)
        approved_count = sum(1 for d in my_drafts if d.status == "approved")
        header.add_row("ARTICLES", f"{article_count} total, {approved_count} approved")
        if any_rejected:
            header.add_row("STATUS", "[red]❌ Some articles rejected — revising[/red]")
        elif all_approved and my_drafts:
            header.add_row("STATUS", "[green]✅ All articles approved[/green]")

        console.print()
        console.print(Panel(header, border_style="cyan", subtitle="📰 Newsroom Desk"))

        # ── Skip checks ─────────────────────────────────────────────────────
        if not my_assignment:
            console.print(Panel(
                "[dim]⏭️  No assignment from the Chief Editor this cycle. Sleeping until called.[/dim]",
                border_style="dim",
                title=f"{display_name} — Idle",
            ))
            return {}

        if all_approved and my_drafts:
            console.print(Panel(
                "[green]✅ All articles already approved by Chief Editor. No further work needed.[/green]",
                border_style="green",
                title=f"{display_name} — Done",
            ))
            return {}

        # ── Assignment brief ────────────────────────────────────────────────
        brief = Table.grid(padding=(0, 1))
        brief.add_column(style="bold yellow")
        brief.add_row(f"[bold]Assignment:[/bold] {my_assignment['topic']}")
        if any_rejected:
            brief.add_row("")
            brief.add_row("[bold red]📝 Chief Editor's Feedback on rejected articles:[/bold red]")
            for fb in rejected_feedback:
                if fb:
                    brief.add_row(f"  [italic]{fb}[/italic]")
        console.print(Panel(brief, border_style="yellow", title=f"{display_name} — Briefing"))

        # ── LLM setup ────────────────────────────────────────────────────────
        context = f"Your Assignment: {my_assignment['topic']}\n"
        if any_rejected:
            context += "\nCHIEF EDITOR FEEDBACK ON PREVIOUS DRAFTS:\n"
            for fb in rejected_feedback:
                if fb:
                    context += f"- {fb}\n"
            context += "Fix these issues in your new set of articles!"
        context += f"\n\nGenerate {ARTICLES_PER_BATCH} distinct, well-researched articles covering different angles of this topic."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context),
        ]

        # ── Research Phase ───────────────────────────────────────────────────
        if tools:
            from app.graph.tools import read_article_content
            active_tools = tools.copy()
            if read_article_content not in active_tools:
                active_tools.append(read_article_content)

            llm_for_research = get_llm(desk_name).bind_tools(active_tools)
            console.print(Panel(
                f"[bold]🔍 {display_name} is now researching the topic...[/bold]\n"
                f"Available tools: {', '.join(t.name for t in active_tools)}",
                border_style="blue",
                title="Research Phase",
            ))

            for step in range(5):
                response = llm_for_research.invoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    reasoning = getattr(response, "content", "") or ""
                    if reasoning:
                        preview = reasoning[:300].replace("\n", " ")
                        console.print(f"  [dim italic]🧠 Thought: \"{preview}\"[/dim italic]")
                    console.print("  [green]✓ No more tool calls needed.[/green]")
                    break

                console.print(f"\n  [bold white]Round {step + 1}/5 — {len(response.tool_calls)} tool call(s):[/bold white]")

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    args_str = _render_tool_args(tool_args)

                    tool_obj: Optional[Callable] = next(
                        (t for t in active_tools if t.name == tool_name), None
                    )

                    if not tool_obj:
                        console.print(f"    [red]✗ Unknown tool '{tool_name}'[/red]")
                        messages.append(
                            ToolMessage(content="Error: Tool not found.", tool_call_id=tool_call["id"])
                        )
                        continue

                    console.print(f"    [cyan]🛠  Calling {tool_name}({args_str})[/cyan]")
                    try:
                        tool_data = tool_obj.invoke(tool_args)
                        summary = _summarise_tool_result(tool_name, tool_data)
                        console.print(f"      [green]{summary}[/green]")
                        messages.append(
                            ToolMessage(content=str(tool_data), tool_call_id=tool_call["id"])
                        )
                    except Exception as e:
                        console.print(f"      [red]💥 Tool call failed: {e}[/red]")
                        messages.append(
                            ToolMessage(content=f"Error: {e}", tool_call_id=tool_call["id"])
                        )

        # ── Writing prompt ──────────────────────────────────────────────────
        articles_instruction = (
            f'You are writing MULTIPLE articles for this section. Generate {ARTICLES_PER_BATCH} articles covering different '
            'subtopics or angles related to your assignment. Each article should have its own headline, '
            'angle, and content. Make them diverse and distinct.\n\n'
            'Respond with ONLY a valid JSON array matching this schema (no markdown, no backticks, no explanation):\n'
            '[\n'
            '  {\n'
            '    "headline": "Compelling headline for the article",\n'
            '    "dek": "One-line subhead summarizing the article",\n'
            '    "summary": "Short 2-3 sentence preview/lede for the article card",\n'
            '    "body_paragraphs": ["Paragraph 1...", "Paragraph 2...", "..."],\n'
            '    "kicker": "Short label e.g. Breaking, Analysis, Opinion (or null)",\n'
            '    "tags": ["tag1", "tag2"],\n'
            '    "sources": [{"name": "Source name", "url": "https://..."}],\n'
            '    "read_time_min": 3,\n'
            '    "image_search_query": "search query for an image (or null)"\n'
            '  },\n'
            '  { ... }\n'
            ']\n\n'
            f'IMPORTANT: Generate exactly {ARTICLES_PER_BATCH} articles. Each should have 4-6 body paragraphs. '
            'Each article must have a unique, distinct headline and topic.'
        )
        messages.append(HumanMessage(content=articles_instruction))

        # ── Article Generation ──────────────────────────────────────────────
        console.print()
        console.print(Panel(
            f"[bold magenta]✍️  {display_name} is writing {ARTICLES_PER_BATCH} articles...[/bold magenta]\n"
            f"Using model: [italic]{byline}[/italic]",
            border_style="magenta",
            title="Writing Phase",
        ))
        try:
            raw_response = get_llm(desk_name).invoke(messages)
            raw_text = raw_response.content.strip() if hasattr(raw_response, "content") else str(raw_response)
            articles_data = _parse_article_json(raw_text)

            # Handle both a single article dict and an array
            if isinstance(articles_data, dict):
                articles_data = [articles_data]
            elif not isinstance(articles_data, list):
                articles_data = []

            new_drafts: List[DraftArticle] = []

            for idx, article_data in enumerate(articles_data):
                draft = DraftArticle(
                    section=desk_name,
                    article_index=idx,
                    author_byline=byline,
                    headline=article_data.get("headline", ""),
                    dek=article_data.get("dek", ""),
                    summary=article_data.get("summary", ""),
                    body_paragraphs=article_data.get("body_paragraphs", []),
                    kicker=article_data.get("kicker"),
                    tags=article_data.get("tags", []),
                    sources=[
                        SourceAttribution(**{k: v for k, v in s.items() if k in ("name", "url", "note")}) 
                        if isinstance(s, dict) else s for s in article_data.get("sources", [])
                    ],
                    read_time_min=article_data.get("read_time_min", 3),
                    image_search_query=article_data.get("image_search_query"),
                )

                # ── Image search ────────────────────────────────────────────
                if getattr(draft, "image_search_query", None):
                    console.print()
                    console.print(Panel(
                        f"[bold blue]🔍 Searching image for: \"{draft.image_search_query}\"[/bold blue]",
                        border_style="blue",
                        title="Image Search",
                    ))
                    from app.graph.tools import fetch_image_duckduckgo
                    try:
                        img_data = fetch_image_duckduckgo.invoke({"query": draft.image_search_query})
                        if img_data and img_data.get("src"):
                            art = ArticleImage(
                                src=img_data["src"],
                                alt=img_data.get("alt", ""),
                                caption=img_data.get("caption", ""),
                                credit=img_data.get("credit", "DuckDuckGo"),
                            )
                            draft.images.append(art)
                            console.print(f"    [green]🖼️  Image attached: {img_data['src'][:80]}...[/green]")
                        else:
                            console.print("    [yellow]⚠️  No image found for query.[/yellow]")
                    except Exception as img_e:
                        console.print(f"    [red]💥 Image search failed: {img_e}[/red]")

                new_drafts.append(draft)

            # ── Draft summary Panel ──────────────────────────────────────────
            for i, draft in enumerate(new_drafts):
                para_count = len(draft.body_paragraphs)
                body_preview = "\n\n".join(draft.body_paragraphs[:2])
                if para_count > 2:
                    body_preview += "\n\n[dim]…[/dim]"

                detail_table = Table.grid(padding=(0, 2))
                detail_table.add_column(style="bold", justify="right")
                detail_table.add_column()
                detail_table.add_row("#", str(i + 1))
                detail_table.add_row("Headline", f"[bold]{draft.headline}[/bold]")
                detail_table.add_row("Subtitle", draft.dek)
                detail_table.add_row("Kicker", draft.kicker or "[dim]none[/dim]")
                detail_table.add_row("Byline", draft.author_byline)
                detail_table.add_row("Body", f"{para_count} paragraph{'s' if para_count != 1 else ''}")
                detail_table.add_row("Tags", ", ".join(draft.tags) if draft.tags else "[dim]none[/dim]")
                detail_table.add_row("Read time", f"{draft.read_time_min} min")
                detail_table.add_row("Sources", str(len(draft.sources)) if draft.sources else "[dim]none[/dim]")
                detail_table.add_row("Images", str(len(draft.images)) if draft.images else "[dim]none[/dim]")

                if draft.body_paragraphs:
                    console.print(Panel(
                        detail_table,
                        border_style="green",
                        title=f"✅ {display_name} — Article #{i + 1} Complete",
                        subtitle=f"📄 {para_count} paragraphs",
                    ))
                    console.print(Panel(
                        body_preview,
                        border_style="bright_green",
                        title="📝 Body Preview",
                    ))
                else:
                    console.print(Panel(
                        detail_table,
                        border_style="yellow",
                        title=f"⚠️  {display_name} — Article #{i + 1} (no body_paragraphs)",
                    ))

            console.print(Panel(
                f"[bold green]✅ {display_name} generated {len(new_drafts)} article(s)[/bold green]",
                border_style="green",
                title="Batch Complete",
            ))

            return {"drafts": new_drafts}

        except Exception as e:
            console.print(Panel(
                f"[bold red]💥 {display_name} encountered an error:[/bold red]\n{str(e)}",
                border_style="red",
                title="Error",
            ))
            errors = state.get("errors", [])
            errors.append({"desk": desk_name, "error": str(e)})
            return {"errors": errors}

    return desk_node
