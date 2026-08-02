"""``issues`` collection — Publisher writes; frontend reads via onSnapshot."""

from __future__ import annotations

from firebase.firebase import db


def read_issue(date: str) -> dict | None:
    snap = db().collection("issues").document(date).get()
    return snap.to_dict() if snap.exists else None


def write_issue(date: str, doc: dict) -> None:
    """Write today's issue (Publisher node only)."""
    db().collection("issues").document(date).set(doc)