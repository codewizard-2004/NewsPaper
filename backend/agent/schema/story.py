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