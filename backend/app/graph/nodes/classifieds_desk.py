from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import CLASSIFIEDS_DESK_PROMPT
from app.graph.tools import fetch_dev_to_articles

classifieds_desk_node = create_desk_node(
    desk_name="classifieds_desk",
    byline="Llama-3-8B",
    system_prompt=CLASSIFIEDS_DESK_PROMPT,
    tools=[fetch_dev_to_articles]
)
