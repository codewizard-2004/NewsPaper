"""Firebase client initialization for the Kernel Gazette.

The ONLY module that imports ``firebase_admin`` and owns app/client creation.
Importing this module never touches the network; the first real Firestore call
triggers initialization, so a missing credential surfaces as a clear
``RuntimeError`` at call-time, never a crash at import-time.
"""

from __future__ import annotations

import hashlib
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

# External clients, re-exported for the rest of the app.
import firebase_admin as firebase  # noqa: E402
from firebase_admin import credentials, firestore  # noqa: E402


def story_hash(url: str) -> str:
    """Standard hash (sha256 of canonical URL), a stable cross-run primary key."""
    return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()


def _credential():
    cert_path = (
        os.getenv("FIREBASE_SERVICE_ACCOUNT")
        or os.getenv("FIREBASE_CREDENTIALS_PATH")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if cert_path and os.path.exists(cert_path):
        return credentials.Certificate(cert_path)
    return None


@lru_cache(maxsize=1)
def _init() -> None:
    """Lazily initialize the Firebase app once (safe to call repeatedly)."""
    if not firebase._apps:  # noqa: SLF001
        cred = _credential()
        if cred:
            firebase.initialize_app(cred)
        else:
            # Application Default Credentials (gcloud auth, metadata server, etc.).
            firebase.initialize_app()


@lru_cache(maxsize=1)
def db():
    """Return the Firestore client, initializing the app on first use."""
    _init()
    return firestore.client()