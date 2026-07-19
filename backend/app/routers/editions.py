import json
import os
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.edition import EditionSchema

router = APIRouter(
    prefix="/editions",
    tags=["editions"],
)

@router.get("/latest", response_model=EditionSchema)
def get_latest_edition():
    """
    Returns the latest edition of the Daily Dispatch.
    For now, this mocks the database by reading the dummy.json file from the frontend.
    """
    try:
        # Resolve path to the frontend's dummy.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Current dir is backend/app/routers, so we go up 3 levels to reach the root, then into frontend/public
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        dummy_path = os.path.join(project_root, "frontend", "public", "dummy.json")
        
        with open(dummy_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load edition: {str(e)}")

@router.post("/generate")
def generate_edition():
    """
    Triggers the LangGraph multi-agent newsroom to generate a new edition.
    """
    from datetime import date
    from app.graph.graph import newsroom_graph
    
    today = date.today().isoformat()
    print(f"\n=======================================================")
    print(f"📰 TRIGGERING NEWSROOM GRAPH FOR {today}")
    print(f"=======================================================")
    
    try:
        final_state = newsroom_graph.invoke({
            "date": today,
            "assignments": [],
            "drafts": [],
            "errors": []
        })
        
        # Here we would normally map the final_state["drafts"] to the EditionSchema
        # and save it to the database.
        
        return {
            "status": "success", 
            "message": "Multi-Agent Newsroom pipeline completed successfully.",
            "drafts_count": len(final_state.get("drafts", []))
        }
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
