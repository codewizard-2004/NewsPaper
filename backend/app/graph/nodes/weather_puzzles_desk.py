from app.graph.nodes.base_desk import create_desk_node
from app.graph.schema.system_prompt import WEATHER_PUZZLES_DESK_PROMPT
from app.graph.tools import fetch_github_trending

weather_puzzles_desk_node = create_desk_node(
    desk_name="weather_puzzles_desk",
    byline="Gemini 2.5 Flash",
    system_prompt=WEATHER_PUZZLES_DESK_PROMPT,
    tools=[fetch_github_trending]
)
