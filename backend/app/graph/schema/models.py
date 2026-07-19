from typing import List, Optional
from pydantic import BaseModel, Field

class SourceAttribution(BaseModel):
    name: str
    url: str
    note: Optional[str] = None

class ArticleImage(BaseModel):
    src: str
    alt: str
    caption: str
    credit: str

class DraftArticle(BaseModel):
    section: str = Field(description="e.g., ai, security, puzzles, business")
    headline: str
    dek: str = Field(description="One-line subhead summarizing the article")
    summary: str = Field(description="3-4 sentence body of the article")
    sources: List[SourceAttribution] = Field(description="Original sources for attribution")
    read_time_min: int = Field(default=3)
    author_byline: str = Field(description="The model's pen name, e.g. 'G. Flash'")
    status: str = Field(default="draft", description="'draft', 'approved', or 'rejected'")
    feedback: Optional[str] = Field(default=None, description="Chief Editor's notes if rejected")
    importance: Optional[int] = Field(default=None, description="1-5 scale assigned by Chief Editor")
    images: List[ArticleImage] = Field(default_factory=list, description="List of images for the article")
    image_search_query: Optional[str] = Field(default=None, description="Provide a clear search query (e.g. 'Elon Musk portrait') to automatically find an image for this article.")

class Assignment(BaseModel):
    desk: str = Field(description="The desk to assign the task to (e.g. 'security_desk')")
    topic: str = Field(description="The specific topic or instruction for the journalist")

class ChiefEditorDecision(BaseModel):
    assignments: List[Assignment] = Field(description="New assignments to dispatch to desks")
    feedback_provided: bool = Field(description="True if you gave feedback to any drafts")
    all_drafts_approved: bool = Field(description="True ONLY if all drafts are marked 'approved'")
