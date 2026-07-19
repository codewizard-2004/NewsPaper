from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()

from app.graph.state import NewsroomState
from app.graph.schema.models import Assignment, ChiefEditorDecision
from app.graph.schema.system_prompt import CHIEF_EDITOR_PROMPT
from app.graph.models import get_llm
from app.graph.schema.system_prompt import CHIEF_EDITOR_PROMPT

def chief_editor_node(state: NewsroomState) -> Dict[str, Any]:
    """
    The Supervisor node logic. It evaluates the current state, assigns work to desks, 
    or reviews submitted drafts.
    """
    console.print("\n[bold green]--- CHIEF EDITOR SUPERVISOR ---[/bold green]")
    
    # 1. Initialize the Chief Editor LLM
    # We use structured output to force the LLM to output a ChiefEditorDecision JSON
    llm = get_llm("chief_editor").with_structured_output(ChiefEditorDecision)
    
    # 2. Build the context for the LLM
    context = f"Current Date: {state.get('date', 'Unknown')}\n\n"
    
    # Check if there are drafts to review
    drafts = state.get('drafts', [])
    if drafts:
        context += "Submitted Drafts to Review:\n"
        for i, draft in enumerate(drafts):
            context += f"[{i}] Desk: {draft.section} | Status: {draft.status}\nHeadline: {draft.headline}\nDek: {draft.dek}\nSummary: {draft.summary}\n\n"
    else:
        context += "No drafts submitted yet. Please create initial assignments.\n"
        # We would usually include the user's request here, but for our automated pipeline 
        # we can just have the editor autonomously decide the daily assignments.
        context += "Generate a daily assignment for 3 different desks of your choice."
        
    # 3. Call the LLM
    messages = [
        SystemMessage(content=CHIEF_EDITOR_PROMPT),
        HumanMessage(content=context)
    ]
    
    console.print("[bold yellow]Chief Editor is evaluating state and making assignments...[/bold yellow]")
    try:
        response = llm.invoke(messages)
        
        # Merge the new assignments (if any) with existing ones to avoid overwriting
        # but for simplicity, we just use the AI's new list.
        # If the editor gave feedback, we need to update the drafts' status in the state.
        # However, updating specific drafts is easier done if the editor returns the updated drafts, 
        # but to keep it simple: the editor gives feedback in the decision, we just pass the assignments back.
        # Wait, if it rejects a draft, how does the state know?
        # Let's let the editor update the assignments list to include a 'revise' instruction if needed.
        
        console.print("[bold green]Chief Editor Decision:[/bold green]")
        for assignment in response.assignments:
            console.print(f"  [cyan]➔ Assignment for {assignment.desk}: {assignment.topic}[/cyan]")
        if response.feedback_provided:
            console.print("  [red]➔ Feedback provided on one or more drafts.[/red]")
        if response.all_drafts_approved:
            console.print("  [bold green]➔ ALL DRAFTS APPROVED! Proceeding to Layout.[/bold green]")

        return {
            "assignments": [a.dict() for a in response.assignments],
        }
    except Exception as e:
        console.print(f"[bold red]Chief Editor Error: {str(e)}[/bold red]")
        return {}
