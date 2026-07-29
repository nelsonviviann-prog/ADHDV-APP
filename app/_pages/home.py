"""Home page - banner, role chooser, clinician passcode gate, and the
educational overview that's safe to show every visitor."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import _assets  # noqa: E402
from _shared import (  # noqa: E402
    RISK_COLORS,
    ROLE_CLINICIAN,
    ROLE_PARENT,
    ROLE_TEACHER,
    app_banner,
    clear_role,
    current_role,
    header,
    is_clinician_authed,
    is_dev_passcode_in_use,
    risk_meter,
    set_role,
    verify_clinician,
)
from src import config as cfg  # noqa: E402
from src.scoring import score  # noqa: E402

header()


# The role-card image box is short and wide (340x132), so object-fit:cover crops
# hard vertically. Faces sit high in these photographs, and the default centred
# crop cuts the tops of heads off -- so each slot carries its own crop position,
# checked against the actual image rather than guessed.
CROP = {
    "role_parent": "center 25%",
    "role_teacher": "center 30%",
    "role_clinician": "center 30%",
}


def role_card(slot: str, body_html: str, accent: str = "#1e3a8a") -> str:
    """A role card, with its illustration on top if one has been added.

    The image is optional. With no file present the card renders exactly as it
    always has, so the app is never broken by a missing asset.
    """
    uri = _assets.data_uri(slot)
    img = (
        f"<img src='{uri}' alt='' style='width:100%; height:132px; "
        f"object-fit:cover; object-position:{CROP.get(slot, 'center')}; "
        f"border-radius:3px; margin-bottom:12px; display:block;'/>"
        if uri else ""
    )
    return (
        f"<div class='role-card' style='height:auto; border-top-color:{accent};'>"
        f"{img}{body_html}</div>"
    )

# ---------------------------------------------------------------------------
# One-shot auto-redirect: when the user clicks "Continue as <role>" or finishes
# the clinician passcode form, we set this session flag and st.rerun(). The
# rerun re-executes streamlit_app.py's build_pages() with the new role, which
# REGISTERS the corresponding page in st.navigation. Only then can we safely
# call st.switch_page -- doing it inside the button handler would fail because
# the target page wasn't registered in the nav at that point.
# ---------------------------------------------------------------------------
_just_picked = st.session_state.pop("_just_picked_role", None)
if _just_picked == ROLE_PARENT:
    st.switch_page("_pages/parent.py")
elif _just_picked == ROLE_TEACHER:
    st.switch_page("_pages/teacher.py")
elif _just_picked == ROLE_CLINICIAN and is_clinician_authed():
    st.switch_page("_pages/clinician.py")

app_banner()

# Optional hero image, directly under the banner. Absent until an image is added.
#
# object-position is 'center 30%', not the default 'center': the subjects' faces
# sit in the upper third, and a centred crop decapitates them at this box ratio.
_hero = _assets.data_uri("hero")
if _hero:
    st.markdown(
        f"<img src='{_hero}' alt='A Nigerian mother and her two children' "
        f"style='width:100%; max-height:360px; object-fit:cover; "
        f"object-position:center 30%; border-radius:6px; margin:0 0 26px 0; "
        f"display:block;'/>",
        unsafe_allow_html=True,
    )

# Animated stat strip -- the first thing a visitor sees move on the page.
st.markdown(
    """
    <div class="stat-strip">
      <div class="stat-tile"><div class="stat-num">37</div>
        <div class="stat-lbl">States + FCT covered</div></div>
      <div class="stat-tile"><div class="stat-num">18</div>
        <div class="stat-lbl">DSM-5 core symptoms</div></div>
      <div class="stat-tile"><div class="stat-num">4&ndash;15</div>
        <div class="stat-lbl">Ages screened</div></div>
      <div class="stat-tile"><div class="stat-num">3</div>
        <div class="stat-lbl">Views: parent, teacher, clinician</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
            role_card(
                "role_parent",
                "<h4>👪 &nbsp;Parent or Caregiver</h4>"
                "<p>Home-context form (33 items). Generates a Study ID to share "
                "with your child's teacher.</p>",
            ),
            unsafe_allow_html=True,
        )
        if st.button("Continue as Parent", type="primary",
                     use_container_width=True, key="pick_parent"):
            set_role(ROLE_PARENT)
            st.session_state["_just_picked_role"] = ROLE_PARENT
            st.rerun()

    with c2:
        st.markdown(
            role_card(
                "role_teacher",
                "<h4 style='color:#7c2d12;'>🏫 &nbsp;Teacher</h4>"
                "<p>Classroom-context form (33 items). Add a teacher rating to "
                "an existing parent screening via Study ID.</p>",
                accent="#7c2d12",
            ),
            unsafe_allow_html=True,
        )
        if st.button("Continue as Teacher", type="primary",
                     use_container_width=True, key="pick_teacher"):
            set_role(ROLE_TEACHER)
            st.session_state["_just_picked_role"] = ROLE_TEACHER
            st.rerun()

    with c3:
        st.markdown(
            role_card(
                "role_clinician",
                "<h4 style='color:#166534;'>⚕️ &nbsp;Clinician</h4>"
                "<p>Cross-informant review of any child by Study ID. "
                "<b>Passcode required.</b></p>",
                accent="#166534",
            ),
            unsafe_allow_html=True,
        )
        if st.button("Continue as Clinician", use_container_width=True, key="pick_clin"):
            set_role(ROLE_CLINICIAN)
            st.rerun()


# ---------------------------------------------------------------------------
# 2. Clinician picked role but not yet verified - show passcode prompt
# ---------------------------------------------------------------------------
elif role == ROLE_CLINICIAN and not is_clinician_authed():
    st.markdown("### Clinician access")
    st.markdown(
        "<div class='info-card' style='border-left-color:#166534;'>"
        "<b>Clinician dashboard is access-coded.</b><br>"
        "Every clinician has a personal access code that maps to their name. "
        "Ask the deployment owner for your code. All actions you take in the "
        "dashboard are logged with your name."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("clinician_auth"):
        pw = st.text_input(
            "Clinician access code",
            type="password",
            autocomplete="off",
            placeholder="e.g. dr-adekoya-7a3b9c",
            help="A personal code given to you by the deployment owner.",
        )
        col_a, col_b = st.columns([1, 5])
        with col_a:
            submit = st.form_submit_button("Sign in", type="primary")
        with col_b:
            cancel = st.form_submit_button("Cancel - pick a different role")

    if cancel:
        clear_role()
        st.rerun()

    if submit:
        if verify_clinician(pw):
            st.session_state["_just_picked_role"] = ROLE_CLINICIAN
            st.success("Verified - opening Clinician Dashboard...")
            st.rerun()
        else:
            st.error("That code isn't on file. Check the code with the deployment owner, "
                     "or pick a different role.")

    if is_dev_passcode_in_use():
        st.caption(
            "⚠️ Deployment is using the **development access code** "
            "(`adhd-2026` → 'Dev Clinician'). The owner should configure real "
            "`clinician_accounts` in Streamlit Cloud → App settings → Secrets "
            "before sharing widely. See README for the TOML format."
        )


# ---------------------------------------------------------------------------
# 3. Role chosen - short welcome + jump-back link
# ---------------------------------------------------------------------------
else:
    target = {
        ROLE_PARENT: ("_pages/parent.py", "Open the Parent Screening form →"),
        ROLE_TEACHER: ("_pages/teacher.py", "Open the Teacher Screening form →"),
        ROLE_CLINICIAN: ("_pages/clinician.py", "Open the Clinician Dashboard →"),
    }[role]

    st.markdown(f"### Welcome - you're using the **{role}** view")
    st.markdown(
        "<p style='color:#57534e;'>Use the sidebar to navigate, or jump straight in:</p>",
        unsafe_allow_html=True,
    )
    st.page_link(target[0], label=target[1])


# ---------------------------------------------------------------------------
# Interactive live demo - visible to everyone. Uses the REAL rule-based scorer
# so a visitor can see how symptom count + impairment drive the risk band,
# without filling the full form. Clearly labelled as a demo, not a screening.
# ---------------------------------------------------------------------------
st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
st.divider()
st.markdown("### Try it - see how the screener thinks")
st.markdown(
    "<p style='color:#57534e; margin-bottom:14px;'>Drag the sliders to sketch a child's "
    "behaviour over the last 6 months. The risk band updates live, using the same DSM-5 "
    "rules as the real screening. <b>This is a demonstration, not a screening.</b></p>",
    unsafe_allow_html=True,
)

d_left, d_right = st.columns([1, 1], gap="large")
with d_left:
    demo_inatt = st.slider(
        "Inattention symptoms seen often (of 9)", 0, 9, 2,
        help="e.g. careless mistakes, not listening, easily distracted, forgetful.",
        key="demo_inatt",
    )
    demo_hyper = st.slider(
        "Hyperactive / impulsive symptoms seen often (of 9)", 0, 9, 2,
        help="e.g. fidgets, cannot stay seated, blurts answers, interrupts.",
        key="demo_hyper",
    )
    demo_impair = st.slider(
        "Areas of life clearly affected (of 8)", 0, 8, 1,
        help="e.g. schoolwork, reading, friendships, family relationships.",
        key="demo_impair",
    )

# Build a partial response dict and run the real scorer. Missing performance
# items default to 3 (average) inside score(), so only the affected areas count.
_demo_responses: dict[str, int] = {}
for i, item in enumerate(cfg.INATTENTION_ITEMS):
    _demo_responses[item] = 4 if i < demo_inatt else 0
for i, item in enumerate(cfg.HYPERACTIVITY_ITEMS):
    _demo_responses[item] = 4 if i < demo_hyper else 0
for i, item in enumerate(cfg.PERFORMANCE_ITEMS):
    _demo_responses[item] = 5 if i < demo_impair else 3
_demo_result = score(_demo_responses)

with d_right:
    st.markdown(risk_meter(_demo_result.risk_level), unsafe_allow_html=True)
    st.markdown(
        f"<div class='info-card' style='border-left-color:"
        f"{RISK_COLORS.get(_demo_result.risk_level, '#1e3a8a')};'>"
        f"<b>{_demo_result.risk_level}</b> &middot; {_demo_result.presentation}<br>"
        f"<span style='color:#57534e; font-size:13px;'>"
        f"{max(demo_inatt, demo_hyper)} symptoms in the stronger subscale &middot; "
        f"{demo_impair} area(s) affected.</span></div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Demonstration only. A real screening asks all 33 questions, pairs parent and "
        "teacher views, and is reviewed by a clinician."
    )


# ---------------------------------------------------------------------------
# Educational overview - visible to everyone, regardless of role state
# ---------------------------------------------------------------------------
st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
st.divider()

left, right = st.columns([1, 1], gap="large")

with left:
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