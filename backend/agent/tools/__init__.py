"""Source tools for the Gazette research node.

One module per source (``hacker_news.py``, ``reddit.py``, ...), a shared
``base.py`` (helpers + :class:`SourceRecord`), and ``sources.py`` which runs
them all in parallel via :func:`fetch_all_sources`.
"""

from agent.tools.base import SourceRecord
from agent.tools.image_search_tool import search_images
from agent.tools.search_tool import search_web
from agent.tools.sources import FETCHERS, fetch_all_sources

__all__ = [
    "SourceRecord",
    "FETCHERS",
    "fetch_all_sources",
    "search_web",
    "search_images",
]