from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import OBITUARIES_BIRTHS_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

obituaries_births_desk_node = create_desk_node(
    desk_name="obituaries_births_desk",
    byline="minimax-m3:cloud",
    system_prompt=OBITUARIES_BIRTHS_DESK_PROMPT,
    tools=ALL_TOOLS
)
