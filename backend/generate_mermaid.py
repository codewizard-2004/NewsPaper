from app.graph.graph import newsroom_graph
import os

png_bytes = newsroom_graph.get_graph().draw_mermaid_png()
output_path = "app/graph.png"

with open(output_path, "wb") as f:
    f.write(png_bytes)
print(f"Graph saved to {output_path}")
