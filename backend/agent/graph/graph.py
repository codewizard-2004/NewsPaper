"""StateGraph construction for the Kernel Gazette.

Linear spine: Research -> Filter -> Editor -> Publisher.
Four journalists fan out from Editor and fan back in to Publisher.

Graph topology (edges / routing) is defined HERE and is stable. Node bodies are
imported from ``agent.nodes`` and swapped during Phases 3-6 without touching
the edge structure.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agent.graph.state import GazetteState
from agent.nodes import (
    JOURNALIST_NODES,
    build_journalist,
    editor_node,
    filter_node,
    publisher_node,
    research_node,
)


def build_graph():
    """Assemble the Gazette StateGraph with edges fixed up front."""
    builder = StateGraph(GazetteState)

    builder.add_node("research", research_node)
    builder.add_node("filter", filter_node)
    builder.add_node("editor", editor_node)
    for page, name in JOURNALIST_NODES.items():
        builder.add_node(name, build_journalist(page))
    builder.add_node("publisher", publisher_node)

    builder.add_edge(START, "research")
    builder.add_edge("research", "filter")
    builder.add_edge("filter", "editor")

    # Fan out: editor -> each journalist.
    for name in JOURNALIST_NODES.values():
        builder.add_edge("editor", name)

    # Fan in: each journalist -> publisher -> end.
    for name in JOURNALIST_NODES.values():
        builder.add_edge(name, "publisher")
    builder.add_edge("publisher", END)

    return builder.compile()


newsroom_graph = build_graph()