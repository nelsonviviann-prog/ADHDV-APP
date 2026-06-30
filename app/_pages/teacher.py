"""Teacher screening page (Vanderbilt-style teacher form).

Server-side role gate: even with the direct URL, only Teacher-role visitors
get past the redirect.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import ROLE_TEACHER, current_role, header, run_screening_page  # noqa: E402

if current_role() != ROLE_TEACHER:
    st.warning("This page is for Teachers only. Returning you to Home to pick a role.")
    st.switch_page("_pages/home.py")
    st.stop()

header("Teacher Screening")
run_screening_page("Teacher")