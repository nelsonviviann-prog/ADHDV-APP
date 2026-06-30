"""
Shared helpers used by every Streamlit page: artifact loading, screening-form
rendering, result rendering, and the common header.

Streamlit's multi-page convention discovers any .py file in `app/pages/` and
auto-builds the sidebar. Helpers live here (NOT under app/pages/) so
Streamlit does not treat them as pages.
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg                  # noqa: E402
from src import database as db                 # noqa: E402
from src.hospitals import (                    # noqa: E402
    NIGERIAN_STATES_AND_FCT,
    referral_recommendations,
)
from src.instruments import (                  # noqa: E402
    FORM_INTRO_PARENT,
    FORM_INTRO_TEACHER,
    Question,
    parent_form,
    teacher_form,
)
from src.pdf_report import build_pdf           # noqa: E402
from src.scoring import (                      # noqa: E402
    cross_informant_agreement,
    score as score_responses,
)


RISK_COLORS = {
    "Low Risk": "#166534",       # forest-800 -- calmer than the previous bright green
    "Moderate Risk": "#b45309",  # amber-700  -- editorial amber, not warning-yellow
    "High Risk": "#991b1b",      # crimson-900 -- serious, not alarming-red
}
ACCENT_COLOR = "#1e3a8a"         # navy-900   -- primary brand colour


@st.cache_resource
def load_model():
    if not cfg.MODEL_PATH.exists() or not cfg.META_PATH.exists():
        return None, None
    return joblib.load(cfg.MODEL_PATH), joblib.load(cfg.META_PATH)


def ensure_model_present() -> tuple[object, dict]:
    model, meta = load_model()
    if model is None:
        st.error(
            "Model artifacts are missing. Run training first from a terminal:\n\n"
            "```powershell\n"
            "cd C:\\Users\\hp\\adhd-screening-nigeria\n"
            ".\\.venv\\Scripts\\Activate.ps1\n"
            "python -m src.train\n"
            "```"
        )
        st.stop()
    return model, meta


def header(active_label: str | None = None) -> None:
    st.set_page_config(
        page_title="ADHD Screening - Nigerian Pediatric Tool",
        page_icon=":brain:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        section.main > div { padding-top: 1.2rem; }
        h1, h2, h3, h4 { font-family: Georgia, 'Times New Roman', serif !important;
                         letter-spacing: -0.01em; }
        .pill {
            display: inline-block; padding: 4px 12px; border-radius: 4px;
            font-size: 12px; font-weight: 600; letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .risk-pill-low      { background: #ecfdf5; color: #166534; border: 1px solid #bbf7d0; }
        .risk-pill-moderate { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
        .risk-pill-high     { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
        .info-card {
            background: #ffffff; border: 1px solid #e7e5e4;
            border-left: 4px solid #1e3a8a; padding: 18px 22px;
            border-radius: 4px; margin: 10px 0;
        }
        /* hero role-card */
        .role-card {
            background: #ffffff; border: 1px solid #e7e5e4;
            border-top: 3px solid #1e3a8a; padding: 22px 22px;
            border-radius: 4px; height: 180px;
            box-shadow: 0 1px 2px rgba(28,25,23,0.04);
        }
        .role-card h4 { margin-top: 0; color: #1e3a8a;
                        font-family: Georgia, serif; font-size: 18px; }
        .role-card p  { color: #44403c; margin-bottom: 0; line-height: 1.55; }
        /* sidebar tweaks */
        section[data-testid="stSidebar"] { border-right: 1px solid #e7e5e4; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if active_label:
        st.markdown(f"### {active_label}")


def risk_pill(risk_level: str) -> str:
    cls = "low" if "Low" in risk_level else "high" if "High" in risk_level else "moderate"
    return f'<span class="pill risk-pill-{cls}">{risk_level}</span>'


def app_banner() -> None:
    """Editorial-Navy hero banner. Renders once at the top of the landing page."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
            color: #fafaf9;
            padding: 38px 44px 32px 44px;
            border-radius: 6px;
            margin: 0 0 28px 0;
            border-bottom: 3px solid #b45309;
            box-shadow: 0 2px 8px rgba(28,25,23,0.08);
        ">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:24px; flex-wrap:wrap;">
                <div style="flex:1; min-width:280px;">
                    <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase;
                                opacity:0.75; margin-bottom:8px;">
                        Master's Capstone Research Project &middot; Nigeria
                    </div>
                    <h1 style="font-family:Georgia, 'Times New Roman', serif; font-weight:700;
                                font-size:34px; line-height:1.15; margin:0 0 10px 0; color:#fafaf9;">
                        Early Detection of ADHD<br>
                        <span style="opacity:0.85; font-weight:400;">in the Nigerian Pediatric Population</span>
                    </h1>
                    <div style="font-size:14px; opacity:0.85; line-height:1.5; max-width:640px;">
                        A non-diagnostic screening and referral support tool for parents,
                        teachers, and primary health workers. DSM-5 aligned &middot; NICHQ
                        Vanderbilt-adapted &middot; covers all 36 states and the FCT.
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
                    <span style="background:#b45309; color:#fafaf9; padding:6px 12px; border-radius:4px;
                                 font-size:11px; letter-spacing:0.08em; text-transform:uppercase; font-weight:600;">
                        Screening &middot; Not Diagnosis
                    </span>
                    <span style="background:rgba(250,250,249,0.15); color:#fafaf9; padding:6px 12px;
                                 border-radius:4px; font-size:11px; letter-spacing:0.05em;">
                        Ages 4 &ndash; 15
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demographics_block(
    *, default_state: str = "Lagos", key_prefix: str = "demo"
) -> dict:
    st.markdown("#### Child demographics")
    c1, c2, c3 = st.columns(3)
    with c1:
        study_id = st.text_input(
            "Child Study ID (optional)",
            help="Re-enter the ID printed on a previous report to add a follow-up screening for the same child.",
            key=f"{key_prefix}_study_id",
        )
        age = st.number_input("Age (years)", min_value=4, max_value=15, value=8, key=f"{key_prefix}_age")
    with c2:
        first = st.text_input("Child's first initial", max_chars=2, value="A", key=f"{key_prefix}_fi")
        gender = st.selectbox("Gender", ["Male", "Female"], key=f"{key_prefix}_gender")
    with c3:
        last = st.text_input("Child's last initial", max_chars=2, value="B", key=f"{key_prefix}_li")
        school_level = st.selectbox(
            "School level",
            list(cfg.SCHOOL_MAP.keys()),
            index=1,
            key=f"{key_prefix}_school",
        )
    state = st.selectbox(
        "State of residence",
        NIGERIAN_STATES_AND_FCT,
        index=NIGERIAN_STATES_AND_FCT.index(default_state),
        key=f"{key_prefix}_state",
    )
    return {
        "study_id": study_id.strip() or None,
        "first_name_initial": (first or "").upper()[:1],
        "last_name_initial": (last or "").upper()[:1],
        "age": int(age),
        "gender": gender,
        "school_level": school_level,
        "state": state,
    }


def _likert_select(label: str, key: str) -> int:
    choice = st.select_slider(
        label,
        options=list(cfg.LIKERT_OPTIONS.keys()),
        value="Sometimes (2)",
        key=key,
    )
    return cfg.LIKERT_OPTIONS[choice]


def _perf_select(label: str, key: str) -> int:
    choice = st.select_slider(
        label,
        options=list(cfg.PERFORMANCE_OPTIONS.keys()),
        value="Average (3)",
        key=key,
    )
    return cfg.PERFORMANCE_OPTIONS[choice]


def render_questionnaire(form_name: str, key_prefix: str) -> dict:
    """Render the right Vanderbilt-style form and return {item_id: response}."""
    if form_name == "parent":
        questions: list[Question] = parent_form()
        st.info(FORM_INTRO_PARENT)
    else:
        questions = teacher_form()
        st.info(FORM_INTRO_TEACHER)

    by_section: dict[str, list[Question]] = {}
    for q in questions:
        by_section.setdefault(q.section, []).append(q)

    section_titles = {
        "inattention": "Section A - Inattention (9 items)",
        "hyperactivity": "Section B - Hyperactivity / Impulsivity (9 items)",
        "performance": "Section C - Performance & Impairment (8 items)",
        "odd": "Section D - Behavioural concerns (4 items)",
        "anxiety": "Section E - Mood & Anxiety (3 items)",
    }
    expander_default = {"inattention": True, "hyperactivity": True,
                        "performance": True, "odd": False, "anxiety": False}

    responses: dict[str, int] = {}
    for section, qs in by_section.items():
        with st.expander(section_titles[section], expanded=expander_default[section]):
            for q in qs:
                key = f"{key_prefix}_{q.item_id}"
                if q.scale == "performance":
                    responses[q.item_id] = _perf_select(q.prompt, key)
                else:
                    responses[q.item_id] = _likert_select(q.prompt, key)
    return responses


def predict_ml(child: dict, responses: dict, rater_type: str, model, meta) -> tuple[str, dict]:
    row = {
        "Age": child["age"],
        "Gender": meta["gender_mapping"].get(child["gender"], 0),
        "School_Level": meta["school_mapping"].get(child["school_level"], 1),
        "Rater_Type": meta["rater_mapping"].get(rater_type, 0),
    }
    for k in cfg.CORE_SYMPTOM_ITEMS + cfg.PERFORMANCE_ITEMS + cfg.ODD_ITEMS + cfg.ANXIETY_ITEMS:
        row[k] = int(responses.get(k, 0))
    X = pd.DataFrame([row])[meta["features"]]
    class_id = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    return (
        meta["risk_mapping"].get(class_id, "Unknown"),
        {meta["risk_mapping"][i]: float(p) for i, p in enumerate(probs)},
    )


def render_result(result, ml_risk: str, ml_probs: dict, child: dict, rater_type: str) -> None:
    st.markdown("### Screening result")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rule-based risk", result.risk_level)
    m2.metric("ML model risk", ml_risk)
    m3.metric("Inattention symptoms", f"{result.inattention_endorsed} / 9")
    m4.metric("Hyperactivity / Impulsivity", f"{result.hyperactivity_endorsed} / 9")

    st.markdown(
        f"<div class='info-card'><b>DSM-5 presentation:</b> {result.presentation}<br>"
        f"<b>Impaired performance areas:</b> {result.impairment_count} / 8</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Reasoning"):
        for e in result.explanation:
            st.write(f"- {e}")

    if result.flags:
        st.markdown("#### Co-occurring concerns")
        for f in result.flags:
            color = "#dc2626" if f["severity"] == "High" else "#d97706"
            st.markdown(
                f"<div class='info-card' style='border-left-color:{color}'>"
                f"<b>[{f['severity']}] {f['domain']}</b><br>{f['message']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("#### ML probability breakdown")
    proba_df = pd.DataFrame(
        {"Risk Level": list(ml_probs.keys()), "Probability": list(ml_probs.values())}
    ).set_index("Risk Level")
    st.bar_chart(proba_df)

    st.markdown("#### Recommended referrals (nearest tertiary facilities)")
    refs = referral_recommendations(child["state"])
    if not refs:
        st.warning(f"No tertiary hospital configured for {child['state']}. Consult the nearest Federal Medical Centre.")
    else:
        rows = [{
            "Hospital": f"{h.name} ({h.abbreviation})",
            "City": h.city,
            "State": h.state,
            "Type": {
                "federal_neuro_psychiatric": "Federal Neuro-Psychiatric",
                "federal_teaching": "Federal Teaching",
                "state_teaching": "State Teaching",
                "specialist": "Specialist",
            }.get(h.kind, h.kind),
        } for h in refs]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.warning(
        "**Reminder:** Screening result only - NOT a diagnosis. ADHD diagnosis "
        "requires direct evaluation by a qualified child psychiatrist or "
        "pediatrician. Bring the downloaded report with you to the referral."
    )


def render_pdf_download(child: dict, parent_result=None, teacher_result=None) -> None:
    pdf_bytes = build_pdf(
        child=child,
        parent_result=parent_result,
        teacher_result=teacher_result,
    )
    st.download_button(
        "Download clinician PDF report",
        data=pdf_bytes,
        file_name=f"adhd_screening_{child.get('study_id','child')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )


def save_session_to_db(child_row: dict, responses: dict, result, rater_type: str,
                       ml_risk: str, rater_contact: str | None) -> int:
    return db.save_session(
        child_id=child_row["id"],
        rater_type=rater_type,
        rater_contact=rater_contact,
        responses=responses,
        result=result,
        ml_prediction=ml_risk,
    )


def run_screening_page(rater_type: str) -> None:
    """Shared body for both Parent and Teacher pages."""
    model, meta = ensure_model_present()
    db.init_db()

    st.markdown(f"#### {rater_type} screening form")
    st.write(
        "Fill in the child's basic information and answer every behavioural item. "
        "All data is stored locally on this device only."
    )

    child_input = render_demographics_block(key_prefix=rater_type.lower())
    rater_contact = st.text_input(
        f"{rater_type} contact (optional)",
        help="A phone number for the parent, or a school name for the teacher. "
             "Stored locally only and only used to help the clinician reach you.",
        key=f"{rater_type.lower()}_contact",
    )

    responses = render_questionnaire(
        "parent" if rater_type == "Parent" else "teacher",
        key_prefix=rater_type.lower(),
    )

    if not st.button(f"Submit {rater_type} screening", type="primary", use_container_width=True):
        return

    result = score_responses(responses)
    ml_risk, ml_probs = predict_ml(child_input, responses, rater_type, model, meta)

    child_row = db.upsert_child(
        study_id=child_input["study_id"],
        first_name_initial=child_input["first_name_initial"],
        last_name_initial=child_input["last_name_initial"],
        age=child_input["age"],
        gender=child_input["gender"],
        school_level=child_input["school_level"],
        state=child_input["state"],
    )
    save_session_to_db(child_row, responses, result, rater_type, ml_risk, rater_contact or None)

    st.success(
        f"Screening saved for Study ID **{child_row['study_id']}**. Share this ID with the "
        f"{'teacher' if rater_type == 'Parent' else 'parent'} so they can add their rating "
        f"for the same child."
    )

    render_result(result, ml_risk, ml_probs, child_row, rater_type)

    other_role = "Teacher" if rater_type == "Parent" else "Parent"
    other_session = db.latest_parent_and_teacher(child_row["id"])
    paired = (other_session[1] if rater_type == "Parent" else other_session[0])
    if paired:
        st.markdown("### Cross-informant agreement")
        from src import scoring  # avoid circular
        other_responses = __import__("json").loads(paired["responses_json"])
        other_result = scoring.score(other_responses)
        if rater_type == "Parent":
            agreement = cross_informant_agreement(result, other_result)
        else:
            agreement = cross_informant_agreement(other_result, result)
        st.markdown(
            f"<div class='info-card'><b>{agreement['agreement']}</b> | "
            f"Parent: {agreement['parent_risk']} | "
            f"Teacher: {agreement['teacher_risk']}</div>",
            unsafe_allow_html=True,
        )
        for note in agreement["notes"]:
            st.write(f"- {note}")
        render_pdf_download(
            child_row,
            parent_result=result if rater_type == "Parent" else other_result,
            teacher_result=other_result if rater_type == "Parent" else result,
        )
    else:
        st.info(
            f"No {other_role.lower()} rating on file yet. Ask the {other_role.lower()} "
            f"to open the **{other_role} Screening** page and enter Study ID "
            f"**{child_row['study_id']}** to add their view."
        )
        render_pdf_download(
            child_row,
            parent_result=result if rater_type == "Parent" else None,
            teacher_result=result if rater_type == "Teacher" else None,
        )
