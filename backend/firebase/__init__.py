"""Firebase access layer for the Kernel Gazette.

This package is the ONE place that imports ``firebase_admin`` and talks to
Firebase. ``firebase.py`` initializes and exposes the app + clients; collection
modules in this folder express the per-collection reads/writes. Node-level
ownership (per ``agents.md``):

- Filter reads ``seen_stories`` only.
- Misc journalist owns ``dsa_bank`` + ``comic_state``.
- Publisher is the only writer of ``issues`` and ``seen_stories``.
"""

from firebase.comic import get_comic_state, save_comic_state
from firebase.dsa import get_next_dsa_question, mark_dsa_used
from firebase.firebase import db, firestore, firebase, story_hash
from firebase.issues import read_issue, write_issue
from firebase.seen import get_seen, mark_published

__all__ = [
    # clients
    "firebase",
    "firestore",
    "db",
    # helpers
    "story_hash",
    # seen_stories
    "get_seen",
    "mark_published",
    # issues
    "read_issue",
    "write_issue",
    # dsa_bank
    "get_next_dsa_question",
    "mark_dsa_used",
    # comic_state
    "get_comic_state",
    "save_comic_state",
]