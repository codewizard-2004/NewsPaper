from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import CLASSIFIEDS_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

classifieds_desk_node = create_desk_node(
    desk_name="classifieds_desk",
    byline="m3:cloud",
    system_prompt=CLASSIFIEDS_DESK_PROMPT,
    tools=ALL_TOOLS
)
