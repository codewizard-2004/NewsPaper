from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import AI_ML_DESK_PROMPT
from app.graph.tools import fetch_reddit_technology, fetch_theverge_rss

ai_ml_desk_node = create_desk_node(
    desk_name="ai_ml_desk",
    byline="GPT-4o-nano",
    system_prompt=AI_ML_DESK_PROMPT,
    tools=[fetch_reddit_technology, fetch_theverge_rss]
)
