from langgraph.graph import StateGraph, START, END
from app.graph.state import NewsroomState
from app.graph.nodes.front_desk import front_desk_node
from app.graph.nodes.supervisor import chief_editor_node
from app.graph.nodes.economics_desk import economics_desk_node
from app.graph.nodes.ai_ml_desk import ai_ml_desk_node
from app.graph.nodes.classifieds_desk import classifieds_desk_node
from app.graph.nodes.weather_puzzles_desk import weather_puzzles_desk_node
from app.graph.nodes.obituaries_births_desk import obituaries_births_desk_node
from app.graph.nodes.sports_desk import sports_desk_node

def build_newsroom_graph():
    """
    Constructs the Supervisor-Worker graph for the Daily Dispatch.
    """
    # 1. Initialize Graph
    builder = StateGraph(NewsroomState)
    
    # 2. Add Nodes
    builder.add_node("Chief_Editor", chief_editor_node)
    builder.add_node("Front_Desk", front_desk_node)
    builder.add_node("Economics_Desk", economics_desk_node)
    builder.add_node("AI_ML_Desk", ai_ml_desk_node)
    builder.add_node("Classifieds_Desk", classifieds_desk_node)
    builder.add_node("Weather_Puzzles_Desk", weather_puzzles_desk_node)
    builder.add_node("Obituaries_Births_Desk", obituaries_births_desk_node)
    builder.add_node("Sports_Desk", sports_desk_node)
    
    # 3. Define Edges (The Workflow)
    # The graph always starts with the Chief Editor writing assignments
    builder.add_edge(START, "Chief_Editor")
    
    # The Chief Editor routes to the desks based on the assignments in the state.
    # In a full supervisor pattern, we use a conditional edge to route to the specific desks 
    # that received an assignment, and then route back to the Editor when done.
    
    # For now, we will add conditional edges to run all desks in parallel, 
    # and they will internally skip if they have no assignments.
    desks = [
        "Front_Desk", 
        "Economics_Desk", 
        "AI_ML_Desk", 
        "Classifieds_Desk", 
        "Weather_Puzzles_Desk", 
        "Obituaries_Births_Desk",
        "Sports_Desk"
    ]
    
    def router(state: NewsroomState):
        """
        Determines if we are done (all drafts approved) or if we need to send 
        assignments to the desks.
        """
        drafts = state.get('drafts', [])
        # If we have 3 approved drafts, we are done (for a 3-article edition)
        approved = [d for d in drafts if d.status == "approved"]
        if len(approved) >= 3:
            return "__end__"
        
        # Otherwise, send to all desks (they will ignore if no assignment)
        return desks

    # The Chief Editor conditionally routes to END or to the Desks
    builder.add_conditional_edges("Chief_Editor", router, {
        "__end__": END,
        **{desk: desk for desk in desks}
    })
    
    # All desks route back to the Chief Editor for review
    for desk in desks:
        builder.add_edge(desk, "Chief_Editor")
        
    return builder.compile()

# We compile the graph instance so it can be imported in the FastAPI router
newsroom_graph = build_newsroom_graph()
