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


def _credential_path() -> str | None:
    return (
        os.getenv("FIREBASE_SERVICE_ACCOUNT")
        or os.getenv("FIREBASE_CREDENTIALS_PATH")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )


def _credential():
    cert_path = _credential_path()
    if cert_path and os.path.exists(cert_path):
        return credentials.Certificate(cert_path)
    return None


def _no_credentials() -> bool:
    """True if no local service-account file AND no well-known ADC file exists.

    When this is True we short-circuit *before* touching the SDK, avoiding a
    slow (~12s) default-credentials metadata probe that would otherwise fire on
    every call during local dev without Firebase access.
    """
    if _credential_path():
        return False
    well_known = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    return not os.path.exists(well_known)


@lru_cache(maxsize=1)
def _init() -> None:
    """Lazily initialize the Firebase app once (safe to call repeatedly)."""
    if _no_credentials():
        raise RuntimeError(
            "No Firebase credentials found. Set FIREBASE_SERVICE_ACCOUNT or "
            "GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON, or run "
            "`gcloud auth application-default login`."
        )
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