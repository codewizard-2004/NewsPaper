from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import FRONT_DESK_PROMPT
from app.graph.tools import fetch_hacker_news_top, fetch_techcrunch_rss

front_desk_node = create_desk_node(
    desk_name="front_desk",
    byline="Llama-3 (Groq)",
    system_prompt=FRONT_DESK_PROMPT,
    tools=[fetch_hacker_news_top, fetch_techcrunch_rss]
)
