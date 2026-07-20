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
    section: str = Field(default="", description="e.g., ai_ml, security, front_desk, economics_desk")
    article_index: int = Field(default=0, description="Index to distinguish multiple articles from the same desk (0, 1, 2, ...)")
    headline: str = Field(default="", description="Compelling, click-worthy headline for the article")
    dek: str = Field(default="", description="One-line subhead summarizing the article")
    summary: str = Field(default="", description="A short 2-3 sentence preview/lede for the article card")
    body_paragraphs: List[str] = Field(default_factory=list, description="The full article body as a list of paragraphs — each string is one paragraph. Write 4-6 substantial paragraphs.")
    kicker: Optional[str] = Field(default=None, description="Short label or tagline displayed above the headline, e.g. 'Breaking', 'Analysis', 'Opinion'")
    tags: List[str] = Field(default_factory=list, description="Relevant topic tags for the article")
    sources: List[SourceAttribution] = Field(default_factory=list, description="Original sources for attribution")
    read_time_min: int = Field(default=3)
    author_byline: str = Field(default="", description="The model's pen name, e.g. 'G. Flash'")
    status: str = Field(default="draft", description="'draft', 'approved', or 'rejected'")
    feedback: Optional[str] = Field(default=None, description="Chief Editor's notes if rejected")
    importance: Optional[int] = Field(default=None, description="1-5 scale assigned by Chief Editor")
    images: List[ArticleImage] = Field(default_factory=list, description="List of images for the article")
    image_search_query: Optional[str] = Field(default=None, description="Provide a clear search query (e.g. 'Elon Musk portrait') to automatically find an image for this article.")

class Assignment(BaseModel):
    desk: str = Field(description="The desk to assign the task to (e.g. 'security_desk')")
    topic: str = Field(description="The specific topic or instruction for the journalist")

class DraftReview(BaseModel):
    section: str = Field(description="The desk/section this review applies to")
    headline: str = Field(default="", description="The headline of the specific article being reviewed (empty if desk only has one article)")
    approved: bool = Field(description="True if the draft is accepted, False if it needs revision")
    feedback: Optional[str] = Field(default=None, description="Constructive criticism if rejected")
    importance: Optional[int] = Field(default=None, description="1-5 importance score for the article (only set if approved)")

class ChiefEditorDecision(BaseModel):
    assignments: List[Assignment] = Field(description="New assignments to dispatch to desks")
    reviews: List[DraftReview] = Field(default_factory=list, description="Per-draft reviews — include article headline to identify which draft is being reviewed when a desk has multiple articles")
    all_drafts_approved: bool = Field(description="True ONLY if every submitted draft is approved")
