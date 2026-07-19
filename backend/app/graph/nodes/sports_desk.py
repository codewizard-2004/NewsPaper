from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import SPORTS_DESK_PROMPT
from app.graph.tools import fetch_reddit_technology

sports_desk_node = create_desk_node(
    desk_name="sports_desk",
    byline="Mixtral-8x7b (Groq)",
    system_prompt=SPORTS_DESK_PROMPT,
    tools=[fetch_reddit_technology]
)
