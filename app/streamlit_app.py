"""
ADHD Screening & Referral Support Tool - main landing page.

Streamlit auto-discovers the screening forms under `app/pages/` and renders
them in the sidebar.
"""

from __future__ import annotations

import streamlit as st

from _shared import app_banner, header


def main() -> None:
    header()
    app_banner()

    st.markdown(
        """
        <p style="font-size:16px; line-height:1.6; color:#44403c; margin-bottom:8px;">
        Welcome. This tool helps <strong>parents, teachers, and primary health workers</strong>
        identify children who may benefit from a specialist ADHD evaluation. Screening
        is based on the DSM-5 criteria and the NICHQ Vanderbilt Assessment Scale,
        adapted to the Nigerian healthcare context.
        </p>
        <p style="font-size:14px; color:#57534e; margin-bottom:24px;">
        Pick a role below or use the sidebar to navigate.
        </p>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            """
            <div class='role-card'>
              <h4>👪 &nbsp;Parent or Caregiver</h4>
              <p>Use the home-context form (33 items). Generates a Study ID
              you can share with the child's teacher.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_Parent_Screening.py", label="Open Parent Screening →")
    with c2:
        st.markdown(
            """
            <div class='role-card' style='border-top-color:#7c2d12;'>
              <h4 style='color:#7c2d12;'>🏫 &nbsp;Teacher</h4>
              <p>Use the classroom-context form (33 items). Add a teacher
              rating to an existing parent screening via Study ID.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_Teacher_Screening.py", label="Open Teacher Screening →")
    with c3:
        st.markdown(
            """
            <div class='role-card' style='border-top-color:#166534;'>
              <h4 style='color:#166534;'>⚕️ &nbsp;Clinician</h4>
              <p>Look up any Study ID, review parent + teacher ratings side
              by side, download the PDF report.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_Clinician_Dashboard.py", label="Open Clinician Dashboard →")

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### How the screening works")
        st.markdown(
            """
            1. **Demographics** — age, gender, school level, state of residence.
            2. **18 DSM-5 core symptoms** — 9 inattention + 9 hyperactivity / impulsivity.
            3. **Performance impairment** — 8 areas of academic / social functioning.
            4. **Co-occurring symptoms** — brief ODD and anxiety/mood screen.
            5. **Risk level** — rule-based (DSM-5) + Random Forest ML second opinion.
            6. **Referral** — auto-routed to nearest Nigerian teaching hospital with
               a child & adolescent mental health unit.
            7. **PDF report** — downloadable, designed for the parent to carry to
               the referral appointment.
            """
        )

    with right:
        st.markdown("### What's different from existing tools")
        st.markdown(
            """
            - Built specifically for Nigerian states (all 36 + FCT covered).
            - **Multi-informant**: parent + teacher ratings on the same child, with
              cross-informant agreement scoring (informed by Conners 3 design).
            - **Offline-first**: SQLite local storage, model runs on-device,
              usable in low-connectivity areas.
            - **Transparent**: rule-based DSM-5 scoring shown alongside the ML
              prediction; clinicians can verify the reasoning.
            - **Non-diagnostic by design**: every result reinforces that
              diagnosis requires a qualified specialist.
            """
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.info(
        "**Privacy:** No personally-identifying information leaves this device. "
        "Children are tracked by a short opaque Study ID; only initials are stored."
    )


if __name__ == "__main__":
    main()