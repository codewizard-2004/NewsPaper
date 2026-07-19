from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import ECONOMICS_DESK_PROMPT
from app.graph.tools import fetch_techcrunch_rss, fetch_theverge_rss

economics_desk_node = create_desk_node(
    desk_name="economics_desk",
    byline="Nvidia Nemotron 550B",
    system_prompt=ECONOMICS_DESK_PROMPT,
    tools=[fetch_techcrunch_rss, fetch_theverge_rss]
)
