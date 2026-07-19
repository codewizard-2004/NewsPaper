from pydantic import BaseModel, Field
from typing import List, Optional

class Author(BaseModel):
    name: str
    role: Optional[str] = None
    aiGenerated: bool = False

class Source(BaseModel):
    name: str
    url: str
    note: Optional[str] = None

class Image(BaseModel):
    src: str
    alt: str
    caption: Optional[str] = None
    credit: Optional[str] = None

class ArticleStory(BaseModel):
    id: str
    page: int
    category: str
    importance: int = Field(ge=1, le=5)
    title: str
    subtitle: str
    kicker: Optional[str] = None
    authors: List[Author]
    sourceIds: List[str]
    sources: List[Source]
    images: List[Image] = []
    content: List[str]
    tags: List[str] = []
    publishedAt: str
    readTimeMin: int
    layoutHint: Optional[str] = None

class Page(BaseModel):
    page: int
    template: str
    title: str
    deck: Optional[str] = None
    articles: List[ArticleStory]

class EditionSource(BaseModel):
    id: str
    name: str
    url: str
    description: Optional[str] = None

class EditionCategory(BaseModel):
    id: str
    title: str
    description: Optional[str] = None

class EditionSchema(BaseModel):
    title: str = "The Daily Dispatch"
    subtitle: str = "A paper-first briefing for the tech desk"
    volume: int
    issue: int
    issueDate: str
    sources: List[EditionSource]
    categories: List[EditionCategory]
    pages: List[Page]
