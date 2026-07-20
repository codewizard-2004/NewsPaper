from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import SPORTS_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

sports_desk_node = create_desk_node(
    desk_name="sports_desk",
    byline="minimax-m3:cloud",
    system_prompt=SPORTS_DESK_PROMPT,
    tools=ALL_TOOLS
)
