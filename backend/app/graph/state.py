import operator
from typing import TypedDict, Annotated, List, Optional, Any
from app.graph.schema.models import DraftArticle

def update_drafts(existing: List[DraftArticle], new: List[DraftArticle]) -> List[DraftArticle]:
    draft_dict = {d.section: d for d in existing}
    for d in new:
        draft_dict[d.section] = d
    return list(draft_dict.values())

def update_errors(existing: List[dict], new: List[dict]) -> List[dict]:
    return existing + new

class NewsroomState(TypedDict):
    """
    The shared memory whiteboard for the multi-agent newsroom.
    """
    date: str
    assignments: List[dict]        # Tasks dispatched by Chief Editor
    drafts: Annotated[List[DraftArticle], update_drafts]
    messages: Annotated[List[Any], operator.add]
    errors: Annotated[List[dict], update_errors]
