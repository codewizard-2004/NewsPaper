"""``comic_state`` collection — Misc journalist only (single continuous doc)."""

from __future__ import annotations

from firebase.firebase import db

COMIC_DOC = "current"


def get_comic_state() -> dict | None:
    snap = db().collection("comic_state").document(COMIC_DOC).get()
    return snap.to_dict() if snap.exists else None


def save_comic_state(synopsis: dict) -> None:
    db().collection("comic_state").document(COMIC_DOC).set(synopsis)