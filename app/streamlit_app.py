"""
ADHD Screening & Referral Support Tool — entry point.

Uses `st.navigation()` to build a *role-gated* sidebar:

    No role picked  ->  [Home, About]
    Parent role     ->  [Home, Parent Screening, About]
    Teacher role    ->  [Home, Teacher Screening, About]
    Clinician role  ->  [Home, About]  (Dashboard only appears after passcode)
    Clinician + verified -> [Home, Clinician Dashboard, About]

Parents never see the Teacher tab. Teachers never see the Parent tab.
The public never sees the Clinician Dashboard tab.
"""

from __future__ import annotations

import streamlit as st

from _shared import (
    ROLE_CLINICIAN,
    ROLE_PARENT,
    ROLE_TEACHER,
    current_role,
    is_clinician_authed,
    render_sidebar_role_widget,
)

# Page config must run before any st.* widget; the header() helper also calls
# set_page_config() but Streamlit is fine with the duplicate as long as the
# args don't conflict.
st.set_page_config(
    page_title="ADHD Screening - Nigerian Pediatric Tool",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def build_pages():
    home = st.Page(
        "_pages/home.py", title="Home", icon=":material/home:", default=True,
    )
    about = st.Page(
        "_pages/about.py", title="About & Ethics", icon=":material/info:",
    )
    parent_pg = st.Page(
        "_pages/parent.py", title="Parent Screening",
        icon=":material/family_restroom:", url_path="parent",
    )
    teacher_pg = st.Page(
        "_pages/teacher.py", title="Teacher Screening",
        icon=":material/school:", url_path="teacher",
    )
    clinician_pg = st.Page(
        "_pages/clinician.py", title="Clinician Dashboard",
        icon=":material/medical_information:", url_path="clinician",
    )

    role = current_role()
    pages = [home]
    if role == ROLE_PARENT:
        pages.append(parent_pg)
    elif role == ROLE_TEACHER:
        pages.append(teacher_pg)
    elif role == ROLE_CLINICIAN and is_clinician_authed():
        pages.append(clinician_pg)
    pages.append(about)
    return pages


def main() -> None:
    render_sidebar_role_widget()
    nav = st.navigation(build_pages())
    nav.run()


if __name__ == "__main__":
    main()
else:
    # Streamlit runs the entry script as `__main__`, but exec-style imports in
    # some test harnesses set __name__ to the module name; cover that too.
    main()