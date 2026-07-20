from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import ECONOMICS_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

economics_desk_node = create_desk_node(
    desk_name="economics_desk",
    byline="nemot3cloud",
    system_prompt=ECONOMICS_DESK_PROMPT,
    tools=ALL_TOOLS
)
