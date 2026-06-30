"""
Minimal i18n scaffolding. All user-facing UI strings flow through `t(key)`.
English is the only language shipping today; YO / IG / HA placeholders are
ready for a native-speaker translator to fill in (no code changes needed).

Usage:
    from src.i18n import t, set_language
    set_language('en')
    st.title(t('app_title'))
"""

from __future__ import annotations

SUPPORTED_LANGUAGES = {
    "en": "English",
    "yo": "Yoruba (not yet translated)",
    "ig": "Igbo (not yet translated)",
    "ha": "Hausa (not yet translated)",
}

_DEFAULT = "en"
_current = _DEFAULT


def set_language(code: str) -> None:
    global _current
    if code in SUPPORTED_LANGUAGES:
        _current = code


def current_language() -> str:
    return _current


TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "ADHD Screening & Referral Support Tool",
        "app_tagline": "Nigerian Pediatric Context (Ages 4-15) - Screening, not diagnosis.",
        "nav_home": "Home",
        "nav_parent": "Parent Screening",
        "nav_teacher": "Teacher Screening",
        "nav_clinician": "Clinician Dashboard",
        "nav_about": "About & Ethics",
        "role_parent": "I am a parent or caregiver",
        "role_teacher": "I am a teacher",
        "role_clinician": "I am a clinician",
        "study_id_label": "Child Study ID",
        "study_id_help": "Short opaque ID printed on the screening report. Leave blank to start a new profile.",
        "submit": "Run screening",
        "non_diagnostic_notice": "This tool is a screening aid and is NOT a diagnosis. Always confirm findings with a qualified child psychiatrist or pediatrician.",
        "language": "Language",
    },
    # Placeholders -- a native-speaker reviewer fills these in. The app
    # falls back to English when a key is missing in a non-en map.
    "yo": {},
    "ig": {},
    "ha": {},
}


def t(key: str) -> str:
    return TRANSLATIONS.get(_current, {}).get(key) or TRANSLATIONS["en"].get(key, key)
