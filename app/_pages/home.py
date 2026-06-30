"""Home page — banner, role chooser, clinician passcode gate, and the
educational overview that's safe to show every visitor."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import (  # noqa: E402
    ROLE_CLINICIAN,
    ROLE_PARENT,
    ROLE_TEACHER,
    app_banner,
    clear_role,
    clinician_passcode,
    current_role,
    header,
    is_clinician_authed,
    set_role,
    verify_clinician,
)

header()
app_banner()

role = current_role()


# ---------------------------------------------------------------------------
# 1. Pre-role: show the 3 role buttons
# ---------------------------------------------------------------------------
if role is None:
    st.markdown("### Pick your role to begin")
    st.markdown(
        "<p style='color:#57534e; margin-bottom:18px;'>"
        "You'll only see the screening form relevant to your role. "
        "Clinician access requires a passcode.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            "<div class='role-card'>"
            "<h4>👪 &nbsp;Parent or Caregiver</h4>"
            "<p>Home-context form (33 items). Generates a Study ID to share "
            "with your child's teacher.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Continue as Parent", type="primary",
                     use_container_width=True, key="pick_parent"):
            set_role(ROLE_PARENT)
            st.switch_page("_pages/parent.py")

    with c2:
        st.markdown(
            "<div class='role-card' style='border-top-color:#7c2d12;'>"
            "<h4 style='color:#7c2d12;'>🏫 &nbsp;Teacher</h4>"
            "<p>Classroom-context form (33 items). Add a teacher rating to "
            "an existing parent screening via Study ID.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Continue as Teacher", type="primary",
                     use_container_width=True, key="pick_teacher"):
            set_role(ROLE_TEACHER)
            st.switch_page("_pages/teacher.py")

    with c3:
        st.markdown(
            "<div class='role-card' style='border-top-color:#166534;'>"
            "<h4 style='color:#166534;'>⚕️ &nbsp;Clinician</h4>"
            "<p>Cross-informant review of any child by Study ID. "
            "<b>Passcode required.</b></p>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Continue as Clinician", use_container_width=True, key="pick_clin"):
            set_role(ROLE_CLINICIAN)
            st.rerun()


# ---------------------------------------------------------------------------
# 2. Clinician picked role but not yet verified — show passcode prompt
# ---------------------------------------------------------------------------
elif role == ROLE_CLINICIAN and not is_clinician_authed():
    st.markdown("### Clinician access")
    st.markdown(
        "<div class='info-card' style='border-left-color:#166534;'>"
        "<b>Clinician dashboard is passcode-protected.</b><br>"
        "It shows every screening session saved on this deployment, including "
        "study IDs and rater contact details. Enter the passcode to continue."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("clinician_auth"):
        pw = st.text_input("Clinician passcode", type="password", autocomplete="off")
        col_a, col_b = st.columns([1, 5])
        with col_a:
            submit = st.form_submit_button("Sign in", type="primary")
        with col_b:
            cancel = st.form_submit_button("Cancel — pick a different role")

    if cancel:
        clear_role()
        st.rerun()

    if submit:
        if verify_clinician(pw):
            st.success("Verified — opening Clinician Dashboard...")
            st.switch_page("_pages/clinician.py")
        else:
            st.error("Incorrect passcode. Try again or pick a different role.")

    # Tiny hint only when the deployment is still on the dev passcode
    if clinician_passcode() == "adhd-2026":
        st.caption(
            "⚠️ Deployment is using the **development passcode**. The owner should set "
            "`clinician_passcode` in Streamlit Cloud → App settings → Secrets before sharing widely."
        )


# ---------------------------------------------------------------------------
# 3. Role chosen — short welcome + jump-back link
# ---------------------------------------------------------------------------
else:
    target = {
        ROLE_PARENT: ("_pages/parent.py", "Open the Parent Screening form →"),
        ROLE_TEACHER: ("_pages/teacher.py", "Open the Teacher Screening form →"),
        ROLE_CLINICIAN: ("_pages/clinician.py", "Open the Clinician Dashboard →"),
    }[role]

    st.markdown(f"### Welcome — you're using the **{role}** view")
    st.markdown(
        "<p style='color:#57534e;'>Use the sidebar to navigate, or jump straight in:</p>",
        unsafe_allow_html=True,
    )
    st.page_link(target[0], label=target[1])


# ---------------------------------------------------------------------------
# Educational overview — visible to everyone, regardless of role state
# ---------------------------------------------------------------------------
st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
st.divider()

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
    "**Privacy:** No personally-identifying information leaves this deployment. "
    "Children are tracked by a short opaque Study ID; only initials are stored."
)