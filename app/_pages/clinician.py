"""
Clinician dashboard - lookup any Study ID, review parent + teacher screenings
side by side, view longitudinal sessions, download the PDF report. Every
action is logged to the audit table tagged with the verified clinician's name.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import (  # noqa: E402
    RISK_COLORS,
    ROLE_CLINICIAN,
    clinician_name,
    current_role,
    ensure_model_present,
    header,
    is_clinician_authed,
    log_clinician_action,
    render_pdf_download,
    risk_pill,
)
from src import database as db                                  # noqa: E402
from src.scoring import cross_informant_agreement, score        # noqa: E402

# Server-side gate: hide the dashboard from anyone who isn't a verified
# Clinician — even if they bookmark or guess the /clinician URL.
if current_role() != ROLE_CLINICIAN or not is_clinician_authed():
    st.error("Clinician access required. Returning you to Home.")
    st.switch_page("_pages/home.py")
    st.stop()

header("Clinician Dashboard")
ensure_model_present()
db.init_db()

# Log the dashboard view once per session (avoids spamming the audit log on
# every rerun caused by widget interactions).
if not st.session_state.get("_logged_dashboard_view"):
    log_clinician_action("view_dashboard")
    st.session_state["_logged_dashboard_view"] = True

# ---------- Greeting ----------
name = clinician_name() or "Clinician"
st.markdown(
    f"<div class='info-card' style='border-left-color:#166534;'>"
    f"<b style='font-family:Georgia,serif; font-size:18px;'>Welcome, {name}.</b><br>"
    f"<span style='color:#57534e;'>Every action you take on this page is recorded "
    f"in the audit log tagged with your name.</span></div>",
    unsafe_allow_html=True,
)

st.write(
    "Look up a child's Study ID to see all parent and teacher screenings saved "
    "on this deployment, the cross-informant agreement, and download the "
    "clinician PDF report."
)

c1, c2 = st.columns([2, 1])
with c1:
    study_id = st.text_input("Child Study ID", placeholder="ADHD-NG-XXXXXX").strip().upper()
with c2:
    if st.button("Refresh recent sessions"):
        st.cache_data.clear()


def _result_from_row(row: dict):
    responses = json.loads(row["responses_json"])
    return score(responses)


# ---------- Recent sessions browser ----------
st.markdown("### Recent screenings on this deployment")
recent = db.recent_sessions(limit=25)
if not recent:
    st.info("No screenings saved yet. A parent or teacher must submit one first.")
else:
    rows = []
    for s in recent:
        rows.append({
            "Study ID": s["study_id"],
            "When (UTC)": s["completed_at"],
            "Rater": s["rater_type"],
            "Age": s["age"],
            "Gender": s["gender"],
            "State": s["state"],
            "Risk": s["risk_level"],
            "ML": s["ml_prediction"],
            "Presentation": s["presentation"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()


def _render_audit_log() -> None:
    # Defensive wrapper: a broken audit log should NEVER take down the rest
    # of the dashboard. If anything fails (missing column on an old DB
    # schema, Streamlit API change, anything), show the rest of the page.
    try:
        activity = db.recent_activity(limit=30)
    except Exception as exc:
        st.caption(f"(Audit log unavailable: {type(exc).__name__})")
        return
    if not activity:
        return
    try:
        rows = []
        for a in activity:
            rows.append({
                "When (UTC)": a["occurred_at"] if "occurred_at" in a.keys() else "-",
                "Clinician":  a["clinician_name"] if "clinician_name" in a.keys() else "-",
                "Action":     a["action"] if "action" in a.keys() else "-",
                "Study ID":   (a["target_study_id"] if "target_study_id" in a.keys() else None) or "-",
            })
        with st.expander(f"Audit log - last {len(rows)} clinician action(s)", expanded=False):
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.caption(f"(Audit log render failed: {type(exc).__name__}: {exc})")


# ---------- Detail view for a chosen Study ID ----------
if not study_id:
    _render_audit_log()
    st.stop()

child = db.find_child(study_id)
if not child:
    st.error(f"No child with Study ID **{study_id}** on this deployment.")
    _render_audit_log()
    st.stop()

# Log the lookup (only on first lookup of this Study ID in this session).
_lookup_flag = f"_logged_view_{study_id}"
if not st.session_state.get(_lookup_flag):
    log_clinician_action("view_study", target_study_id=study_id)
    st.session_state[_lookup_flag] = True

st.markdown(f"### Profile - Study ID `{child['study_id']}`")
prof_cols = st.columns(5)
prof_cols[0].metric("Age", child["age"])
prof_cols[1].metric("Gender", child["gender"])
prof_cols[2].metric("School", child["school_level"])
prof_cols[3].metric("State", child["state"])
prof_cols[4].metric("Initials", f"{child['first_name_initial']}.{child['last_name_initial']}.")

sessions = db.sessions_for_child(child["id"])
if not sessions:
    st.warning("Profile exists but has no screening sessions yet.")
    _render_audit_log()
    st.stop()

st.markdown(f"### Longitudinal sessions ({len(sessions)})")
hist_rows = [{
    "When (UTC)": s["completed_at"],
    "Rater": s["rater_type"],
    "Risk (rule-based)": s["risk_level"],
    "ML Risk": s["ml_prediction"],
    "Inattention": s["inatt_endorsed"],
    "H/I": s["hi_endorsed"],
    "Impaired": s["impairment_count"],
    "Presentation": s["presentation"],
} for s in sessions]
st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

# ---------- Cross-informant view ----------
parent_row, teacher_row = db.latest_parent_and_teacher(child["id"])

st.markdown("### Cross-informant view (most recent of each rater)")
col_p, col_t = st.columns(2)


def _render_side(col, row, label):
    with col:
        st.markdown(f"#### {label}")
        if not row:
            st.info(f"No {label.lower()} rating on file.")
            return None
        res = _result_from_row(row)
        st.markdown(risk_pill(res.risk_level), unsafe_allow_html=True)
        st.write(f"**Presentation:** {res.presentation}")
        st.write(f"Inattention endorsed: **{res.inattention_endorsed} / 9**")
        st.write(f"H/I endorsed: **{res.hyperactivity_endorsed} / 9**")
        st.write(f"Impaired performance areas: **{res.impairment_count} / 8**")
        if res.flags:
            with st.expander(f"{len(res.flags)} co-occurring flag(s)"):
                for f in res.flags:
                    st.write(f"**[{f['severity']}] {f['domain']}** - {f['message']}")
        return res


p_res = _render_side(col_p, parent_row, "Parent rating")
t_res = _render_side(col_t, teacher_row, "Teacher rating")

if p_res and t_res:
    st.markdown("### Agreement")
    agreement = cross_informant_agreement(p_res, t_res)
    color = RISK_COLORS.get(p_res.risk_level, "#1e3a8a")
    st.markdown(
        f"<div style='padding:14px;border-radius:6px;border:2px solid {color};"
        f"background:{color}10;'><b>{agreement['agreement']}</b> | "
        f"Parent: {agreement['parent_risk']} | Teacher: {agreement['teacher_risk']}</div>",
        unsafe_allow_html=True,
    )
    for n in agreement["notes"]:
        st.write(f"- {n}")

# ---------- PDF download ----------
st.divider()
st.markdown("### Generate clinician PDF report")
render_pdf_download(child, parent_result=p_res, teacher_result=t_res)
# NOTE: Streamlit's st.download_button fires client-side without a server
# round-trip, so a true "downloaded" event isn't reliably catchable from
# Python. The earlier view_study log already captures the meaningful
# clinician action (they opened this Study ID and saw the PDF button).

st.divider()
_render_audit_log()