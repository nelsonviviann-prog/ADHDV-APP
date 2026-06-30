"""
ADHD Screening & Referral Support Tool - main landing page.

This file is the multi-page Streamlit entry point. Streamlit auto-discovers
the screening forms under `app/pages/` and renders them in the sidebar:

    1_Parent_Screening.py     -> "Parent Screening"
    2_Teacher_Screening.py    -> "Teacher Screening"
    3_Clinician_Dashboard.py  -> "Clinician Dashboard"
    4_About.py                -> "About & Ethics"
"""

from __future__ import annotations

import streamlit as st

from _shared import header


def main() -> None:
    header()

    st.title(":brain: ADHD Screening & Referral Support Tool")
    st.caption(
        "Nigerian Pediatric Context (Ages 4-15) - **Screening tool, not a diagnosis.**"
    )

    st.markdown(
        """
        Welcome. This tool helps **parents, teachers, and primary health workers**
        identify children who may benefit from a specialist ADHD evaluation.
        The screening is based on the DSM-5 criteria and the NICHQ Vanderbilt
        Assessment Scale, adapted to the Nigerian healthcare context.

        Pick a role below or use the sidebar to navigate.
        """
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class='info-card'>
            <b>:family: I am a parent or caregiver</b><br>
            Use the home-context form (47 items). Generates a Study ID
            you can share with the child's teacher.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_Parent_Screening.py", label="Open Parent Screening", icon=":material/family_restroom:")
    with c2:
        st.markdown(
            """
            <div class='info-card' style='border-left-color:#1d4ed8'>
            <b>:school: I am a teacher</b><br>
            Use the classroom-context form (35 items). Add a teacher
            rating to an existing parent screening via Study ID.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_Teacher_Screening.py", label="Open Teacher Screening", icon=":material/school:")
    with c3:
        st.markdown(
            """
            <div class='info-card' style='border-left-color:#7c3aed'>
            <b>:medical_information: I am a clinician</b><br>
            Look up any Study ID, review parent + teacher ratings side
            by side, download the PDF report.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_Clinician_Dashboard.py", label="Open Clinician Dashboard", icon=":material/medical_information:")

    st.divider()

    st.markdown("### How the screening works")
    st.markdown(
        """
        1. **Demographics** - age, gender, school level, state of residence.
        2. **18 DSM-5 core symptoms** - 9 inattention + 9 hyperactivity / impulsivity.
        3. **Performance impairment** - 8 areas of academic / social functioning.
        4. **Co-occurring symptoms** - brief ODD and anxiety/mood screen.
        5. **Risk level** - rule-based (DSM-5) + Random Forest ML second opinion.
        6. **Referral** - auto-routed to nearest Nigerian teaching hospital with
           a child & adolescent mental health unit.
        7. **PDF report** - downloadable, designed for the parent to carry to
           the referral appointment.
        """
    )

    st.markdown("### What's different from existing tools")
    st.markdown(
        """
        - Built specifically for Nigerian states (all 36 + FCT covered).
        - **Multi-informant**: parent + teacher ratings on the same child, with
          cross-informant agreement scoring (informed by Conners 3 design).
        - **Offline-first**: SQLite local storage, model runs on-device, no cloud
          dependency - usable in low-connectivity areas.
        - **Transparent**: rule-based DSM-5 scoring shown alongside the ML
          prediction; clinicians can verify the reasoning.
        - **Non-diagnostic by design**: every result reinforces that diagnosis
          requires a qualified specialist.
        """
    )

    st.info(
        "**Privacy:** No personally-identifying information leaves this device. "
        "Children are tracked by a short opaque Study ID; only initials are stored."
    )


if __name__ == "__main__":
    main()
