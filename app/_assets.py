"""
Optional image assets.

Images live in `assets/images/`. They are OPTIONAL by design: every lookup
falls back cleanly when a file is absent, so the app works with no images at
all, with some of them, or with all of them. Drop a correctly-named file in and
it appears on the next rerun -- no code change needed.

Filenames are fixed. See IMAGES below for the expected name of each slot.
"""

from __future__ import annotations

import base64
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
IMAGE_DIR = APP_DIR.parent / "assets" / "images"

# slot -> filename. Any of these extensions is accepted for a given slot.
EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

IMAGES = {
    "hero":           "hero_children",
    "role_parent":    "role_parent",
    "role_teacher":   "role_teacher",
    "role_clinician": "role_clinician",
    "consult":        "consult_hero",
    "screening":      "screening_banner",   # shared by the Parent + Teacher forms
}

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def find(slot: str) -> Path | None:
    """Path to the image for `slot`, or None if the owner hasn't added one."""
    stem = IMAGES.get(slot)
    if not stem:
        return None
    for ext in EXTENSIONS:
        candidate = IMAGE_DIR / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def has(slot: str) -> bool:
    return find(slot) is not None


def data_uri(slot: str) -> str | None:
    """Base64 data URI, for embedding inside a raw-HTML card.

    Streamlit's st.image() cannot render inside an HTML block, so cards that are
    built as HTML need the bytes inlined instead of a file path.
    """
    path = find(slot)
    if path is None:
        return None
    mime = _MIME.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def missing() -> list[str]:
    """Slots with no image yet -- used to tell the owner what is still needed."""
    return [slot for slot in IMAGES if not has(slot)]
