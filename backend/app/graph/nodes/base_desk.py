import json
from typing import Dict, Any, Callable
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

console = Console()

from app.graph.state import NewsroomState
from app.graph.schema.models import DraftArticle
from app.graph.models import get_llm
from app.graph.tools import fetch_hacker_news_top

def create_desk_node(desk_name: str, byline: str, system_prompt: str, tools: list = []) -> Callable:
    """
    Factory function to create a LangGraph node for a specific journalist desk.
    """
    def desk_node(state: NewsroomState) -> Dict[str, Any]:
        console.print(f"\n[bold cyan]--- DESK: {desk_name.upper()} ---[/bold cyan]")
        
        # 1. Check if the Chief Editor gave us an assignment
        assignments = state.get("assignments", [])
        my_assignment = next((a for a in assignments if a.get("desk") == desk_name), None)
        
        # If no assignment, skip
        drafts = state.get("drafts", [])
        my_draft = next((d for d in drafts if d.section == desk_name), None)
        
        if not my_assignment:
            console.print(f"[dim]{desk_name}: No assignment. Sleeping.[/dim]")
            return {}
            
        if my_draft and my_draft.status == "approved":
            console.print(f"[green]{desk_name}: Draft already approved. Sleeping.[/green]")
            return {}

        # 2. Setup the Agent
        llm = get_llm(desk_name).with_structured_output(DraftArticle)
        
        # 3. Build the Context
        context = f"Your Assignment: {my_assignment['topic']}\n"
        if my_draft and my_draft.status == "rejected" and my_draft.feedback:
            context += f"\nCHIEF EDITOR FEEDBACK ON PREVIOUS DRAFT:\n{my_draft.feedback}\nFix these issues in your new draft!"
            
        # 3.5. Inject Tool Data directly if tools are provided
        if tools:
            console.print(f"[yellow]{desk_name}: Fetching latest news data from sources...[/yellow]")
            context += "\n\n--- LATEST NEWS DATA FROM SOURCES ---\n"
            for tool in tools:
                try:
                    console.print(f"[dim]  ➔ Using tool: {tool.name}[/dim]")
                    tool_data = tool.invoke({"limit": 5})
                    context += f"\nSOURCE: {tool.name}\n{tool_data}\n"
                except Exception as e:
                    console.print(f"[red]  ➔ Failed to execute tool {tool.name}: {e}[/red]")
            context += "--------------------------------------\n"

        # 4. Generate the Article
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context)
        ]
        
        console.print(f"[bold magenta]{desk_name}: Writing article... (Model: {byline})[/bold magenta]")
        try:
            draft = llm.invoke(messages)
            
            # Enforce metadata
            draft.section = desk_name
            draft.author_byline = byline
            draft.status = "draft"
            
            # Auto-fetch image if a query was requested
            if getattr(draft, 'image_search_query', None):
                console.print(f"[bold blue]{desk_name}: Searching image for '{draft.image_search_query}'[/bold blue]")
                from app.graph.tools import fetch_image_duckduckgo
                try:
                    img_data = fetch_image_duckduckgo.invoke({"query": draft.image_search_query})
                    if img_data and img_data.get("src"):
                        from app.graph.schema.models import ArticleImage
                        draft.images.append(ArticleImage(**img_data))
                        console.print(f"[green]  ➔ Image attached: {img_data.get('src')}[/green]")
                except Exception as img_e:
                    console.print(f"[red]  ➔ Image search failed - {img_e}[/red]")
            
            console.print(Panel(
                f"[bold]{draft.headline}[/bold]\n\n{draft.summary}",
                title=f"{desk_name.title()} Draft",
                border_style="cyan"
            ))
            
            # 5. Update State
            return {"drafts": [draft]}
            
        except Exception as e:
            console.print(f"[bold red]{desk_name} ERROR: {str(e)}[/bold red]")
            errors = state.get("errors", [])
            errors.append({"desk": desk_name, "error": str(e)})
            return {"errors": errors}

    return desk_node
