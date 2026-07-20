from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import EDUCATION_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

# Create the Education Desk Node
education_desk_node = create_desk_node(
    desk_name="education_desk",
    byline="minimax-m3:cloud",
    system_prompt=EDUCATION_DESK_PROMPT,
    tools=ALL_TOOLS
)
