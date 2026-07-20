from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import FRONT_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

front_desk_node = create_desk_node(
    desk_name="front_desk",
    byline="nemotloud",
    system_prompt=FRONT_DESK_PROMPT,
    tools=ALL_TOOLS
)
