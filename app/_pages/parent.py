"""Parent screening page (Vanderbilt-style parent form).

Server-side role gate: even with the direct URL, only Parent-role visitors
get past the redirect. Teacher- or Clinician-role visitors get sent back to
Home.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import ROLE_PARENT, current_role, header, run_screening_page  # noqa: E402

if current_role() != ROLE_PARENT:
    st.warning("This page is for Parents only. Returning you to Home to pick a role.")
    st.switch_page("_pages/home.py")
    st.stop()

header("Parent / Caregiver Screening")
run_screening_page("Parent")