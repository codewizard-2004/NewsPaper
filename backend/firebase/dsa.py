"""``dsa_bank`` collection — Misc journalist only (rotation source)."""

from __future__ import annotations

from firebase.firebase import db


def get_next_dsa_question() -> dict | None:
    """Return the next unused DSA question, or None if the bank is exhausted."""
    docs = list(db().collection("dsa_bank").where(filter=("used", "==", False)).limit(1).stream())
    if not docs:
        return None
    doc = docs[0]
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def mark_dsa_used(qid: str) -> None:
    db().collection("dsa_bank").document(qid).update({"used": True})