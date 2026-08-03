"""Firestore ``issues/{date}`` schema.

The published issue the frontend subscribes to. Item ``type`` drives rendering:
``article``, ``dsa_question``, or ``comic``.
"""

from __future__ import annotations

import math
from typing import List, Union

from pydantic import BaseModel, Field, field_validator


def _finite_rating(value: float) -> float:
    return value if math.isfinite(value) else 0.0


class ArticleItem(BaseModel):
    """A full-length journalist-written article."""

    id: str
    type: str = "article"
    headline: str
    body: str
    sources: List[str] = Field(default_factory=list)
    confidence_rating: float = 0.0
    importance_rating: float = 0.0
    image_url: str | None = None

    _norm_conf = field_validator("confidence_rating")(_finite_rating)
    _norm_imp = field_validator("importance_rating")(_finite_rating)


class DSAItem(BaseModel):
    """A daily DSA practice question in the Misc section."""

    id: str
    type: str = "dsa_question"
    prompt: str
    difficulty: str = "medium"


class ComicItem(BaseModel):
    """The continuing comic strip panel."""

    id: str
    type: str = "comic"
    image_url: str | None = None
    caption: str = ""


class ComicScript(BaseModel):
    """Next strip installment, written by the Misc journalist (task ``write``)."""

    synopsis: str = Field(
        description="1-3 sentence continuation of the arc, advancing the story one beat",
    )
    caption: str = Field(
        description="Short witty caption/tagline for today's panel",
    )


Item = Union[ArticleItem, DSAItem, ComicItem]


class IssueSection(BaseModel):
    """One named page (section) within an issue."""

    name: str
    items: List[Item] = Field(default_factory=list)


class Issue(BaseModel):
    """The full daily issue document."""

    date: str
    sections: List[IssueSection] = Field(default_factory=list)