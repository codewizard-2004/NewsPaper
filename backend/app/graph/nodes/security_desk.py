from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import SECURITY_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

# Create the Security Desk Node
security_desk_node = create_desk_node(
    desk_name="security_desk",
    byline="necloud",
    system_prompt=SECURITY_DESK_PROMPT,
    tools=ALL_TOOLS
)
