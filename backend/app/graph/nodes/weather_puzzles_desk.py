from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import WEATHER_PUZZLES_DESK_PROMPT
from app.graph.tools import ALL_TOOLS

weather_puzzles_desk_node = create_desk_node(
    desk_name="weather_puzzles_desk",
    byline="minimax-m3:cloud",
    system_prompt=WEATHER_PUZZLES_DESK_PROMPT,
    tools=ALL_TOOLS
)
