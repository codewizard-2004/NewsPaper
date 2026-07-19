from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import OBITUARIES_BIRTHS_DESK_PROMPT
from app.graph.tools import fetch_github_trending

obituaries_births_desk_node = create_desk_node(
    desk_name="obituaries_births_desk",
    byline="Minimax M3",
    system_prompt=OBITUARIES_BIRTHS_DESK_PROMPT,
    tools=[fetch_github_trending]
)
