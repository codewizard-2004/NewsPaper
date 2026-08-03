"""Story schemas -- the curated stories flowing Research -> Filter -> Editor."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Story(BaseModel):
    """A single curated story moving through the pipeline.

    - after Research: title/url/score/summary/cluster_sources populated
    - after Editor:  also has ``page`` (bucket) and optionally ``topic``
    - after a journalist: has ``body``, ``confidence_rating``, ``importance_rating``
    """

    title: str
    url: str
    score: float = 0.0
    summary: str = ""
    cluster_sources: List[str] = Field(default_factory=list)

    # Editor
    page: str | None = None
    topic: str | None = None

    # Journalist
    body: str | None = None
    confidence_rating: float | None = None
    importance_rating: float | None = None


# page bucket -> list of stories assigned to it
Categorized = dict[str, List[Story]]


class EditorSelection(BaseModel):
    """Editor's page-assignment judgment (one structured LLM call, task ``edit``).

    Each page holds the *indices* of stories from ``fresh_stories``. The Editor
    node maps indices back to the real story dicts, so the model can never
    invent a story — anything not in the catalog is simply dropped.
    """

    front_page: List[int] = Field(
        default_factory=list,
        description="Indices of the day's most important stories (target 3-10)",
    )
    aiml_page: List[int] = Field(
        default_factory=list,
        description="Indices of AI / machine learning stories (target 3-10)",
    )
    security_page: List[int] = Field(
        default_factory=list,
        description="Indices of security / privacy stories (target 3-10)",
    )
    misc_page: List[int] = Field(
        default_factory=list,
        description="Indices of everything else worth printing (target 3-10)",
    )


class ArticleDraft(BaseModel):
    """A journalist's written piece for one story (task ``write``).

    ``headline`` stays the source title (deterministic, so titles never drift);
    the model only supplies the body and the two ratings.
    """

    body: str = Field(
        description="Full newspaper-style article, 150-350 words, grounded only in the provided research",
    )
    confidence_rating: float = Field(
        description="0.0 to 1.0 — how well-supported the article's facts are by the sources",
    )
    importance_rating: float = Field(
        description="0.0 to 10.0 — how significant this story is for today's paper",
    )