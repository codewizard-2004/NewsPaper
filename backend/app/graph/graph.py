from langgraph.graph import StateGraph, START, END
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from app.graph.state import NewsroomState
from app.graph.nodes.supervisor import chief_editor_node
from app.graph.nodes.front_desk import front_desk_node
from app.graph.nodes.economics_desk import economics_desk_node
from app.graph.nodes.ai_ml_desk import ai_ml_desk_node
from app.graph.nodes.classifieds_desk import classifieds_desk_node
from app.graph.nodes.weather_puzzles_desk import weather_puzzles_desk_node
from app.graph.nodes.obituaries_births_desk import obituaries_births_desk_node
from app.graph.nodes.sports_desk import sports_desk_node
from app.graph.nodes.education_desk import education_desk_node
from app.graph.nodes.security_desk import security_desk_node
from app.graph.nodes.publish import publish_node

console = Console()

# Map graph node names to assignment desk names (snake_case)
NODE_TO_DESK = {
    "Front_Desk": "front_desk",
    "Economics_Desk": "economics_desk",
    "AI_ML_Desk": "ai_ml_desk",
    "Classifieds_Desk": "classifieds_desk",
    "Weather_Puzzles_Desk": "weather_puzzles_desk",
    "Obituaries_Births_Desk": "obituaries_births_desk",
    "Sports_Desk": "sports_desk",
    "Education_Desk": "education_desk",
    "Security_Desk": "security_desk",
}
DESK_TO_NODE = {v: k for k, v in NODE_TO_DESK.items()}

DESK_NODES = [
    ("Front_Desk", front_desk_node),
    ("Economics_Desk", economics_desk_node),
    ("AI_ML_Desk", ai_ml_desk_node),
    ("Classifieds_Desk", classifieds_desk_node),
    ("Weather_Puzzles_Desk", weather_puzzles_desk_node),
    ("Obituaries_Births_Desk", obituaries_births_desk_node),
    ("Sports_Desk", sports_desk_node),
    ("Education_Desk", education_desk_node),
    ("Security_Desk", security_desk_node),
]
ALL_DESK_NODE_NAMES = [n for n, _ in DESK_NODES]

DESK_DISPLAY_NAMES = {n: n.replace("_", " ").title() for n in ALL_DESK_NODE_NAMES}


def build_newsroom_graph():
    """
    Constructs the Supervisor-Worker graph for the Daily Dispatch.
    """
    builder = StateGraph(NewsroomState)

    builder.add_node("Chief_Editor", chief_editor_node)
    for node_name, node_fn in DESK_NODES:
        builder.add_node(node_name, node_fn)
    builder.add_node("Publish", publish_node)

    builder.add_edge(START, "Chief_Editor")

    def router(state: NewsroomState):
        """
        Routes from Chief Editor to desks that need work, or to Publish when all approved.
        Now checks that ALL articles for each desk are approved (not just any one).
        """
        assignments = state.get("assignments", [])
        drafts = state.get("drafts", [])

        assigned_desks = {a.get("desk") for a in assignments if a.get("desk")}

        # A desk is "fully approved" only when ALL its drafts are approved
        def is_desk_fully_approved(desk: str) -> bool:
            desk_drafts = [d for d in drafts if d.section == desk]
            if not desk_drafts:
                return False
            return all(d.status == "approved" for d in desk_drafts)

        fully_approved_desks = {d for d in assigned_desks if is_desk_fully_approved(d)}
        pending_desks = assigned_desks - fully_approved_desks

        # ── Render routing table ────────────────────────────────────────────
        route_table = Table(
            title="🗺️  Routing Decision",
            box=box.ROUNDED,
            border_style="bright_blue",
            show_header=True,
        )
        route_table.add_column("Category", style="bold", width=18)
        route_table.add_column("Details", style="white")

        if not assigned_desks:
            route_table.add_row("[cyan]📌 Assigned[/cyan]", "[dim]None (first pass)[/dim]")
            route_table.add_row("[green]✅ Approved[/green]", "[dim]None[/dim]")
            route_table.add_row("[yellow]⏳ Pending[/yellow]", "[dim]None[/dim]")
            route_table.add_row(
                "[bold]➡️  Routing to[/bold]",
                "[bold]All desks (first pass — Chief Editor just created assignments)[/bold]",
            )
            console.print()
            console.print(Panel(route_table, border_style="bright_blue"))
            return ALL_DESK_NODE_NAMES

        assigned_str = ", ".join(sorted(assigned_desks)) if assigned_desks else "[dim]None[/dim]"
        approved_str = ", ".join(sorted(fully_approved_desks)) if fully_approved_desks else "[dim]None[/dim]"
        pending_str = ", ".join(sorted(pending_desks)) if pending_desks else "[dim]None[/dim]"

        route_table.add_row("[cyan]📌 Assigned[/cyan]", assigned_str)
        route_table.add_row("[green]✅ Approved[/green]", approved_str)

        if pending_desks:
            route_table.add_row("[yellow]⏳ Pending[/yellow]", pending_str)
        else:
            route_table.add_row("[green]⏳ Pending[/green]", "[dim]None — all complete[/dim]")

        if assigned_desks and assigned_desks == fully_approved_desks:
            route_table.add_row(
                "[bold green]➡️  Routing to[/bold green]",
                "[bold green]📰 PUBLISH — All drafts approved![/bold green]",
            )
            console.print()
            console.print(Panel(route_table, border_style="bright_blue"))
            return "Publish"

        if pending_desks:
            desk_nodes_list = [DESK_TO_NODE[d] for d in pending_desks if d in DESK_TO_NODE]
            target_str = ", ".join(DESK_DISPLAY_NAMES.get(n, n) for n in desk_nodes_list)
            route_table.add_row(
                "[bold yellow]➡️  Routing to[/bold yellow]",
                f"[bold yellow]{len(desk_nodes_list)} desk(s): {target_str}[/bold yellow]",
            )
            console.print()
            console.print(Panel(route_table, border_style="bright_blue"))
            return desk_nodes_list if desk_nodes_list else ALL_DESK_NODE_NAMES

        route_table.add_row(
            "[bold]➡️  Routing to[/bold]",
            "[bold]All desks (fallback)[/bold]",
        )
        console.print()
        console.print(Panel(route_table, border_style="bright_blue"))
        return ALL_DESK_NODE_NAMES

    route_map = {"Publish": "Publish", **{n: n for n in ALL_DESK_NODE_NAMES}}
    builder.add_conditional_edges("Chief_Editor", router, route_map)

    for node_name, _ in DESK_NODES:
        builder.add_edge(node_name, "Chief_Editor")

    builder.add_edge("Publish", END)

    return builder.compile()


newsroom_graph = build_newsroom_graph()
