"""
Feedback page - open to everyone, including visitors who have not picked a role.

Feedback is deliberately anonymous: nothing written here is linked to a child,
a Study ID, or a screening session. The optional contact field is the only PII
captured, and only when the user volunteers it to get a reply.

Clinicians read what lands here from the "User feedback" section of the
Clinician Dashboard.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import current_role, header  # noqa: E402
from src import database as db            # noqa: E402

header("Feedback")
db.init_db()

RATING_LABELS = {
    1: "1 - Poor",
    2: "2 - Fair",
    3: "3 - Good",
    4: "4 - Very good",
    5: "5 - Excellent",
}

CATEGORIES = [
    "General impression",
    "Ease of use",
    "The screening questions",
    "Clarity of the result",
    "Referral suggestions",
    "Bug / something broke",
    "Feature request",
    "Other",
]

ROLES = ["Parent", "Teacher", "Clinician", "Health worker", "Researcher", "Other"]

st.markdown(
    "<div class='info-card'>"
    "<b>Tell us how this tool is working for you.</b><br>"
    "<span style='color:#57534e;'>Your feedback shapes how this screening tool develops. "
    "Nothing you write here is linked to a child, a Study ID, or any screening result "
    "&mdash; it is stored anonymously.</span>"
    "</div>",
    unsafe_allow_html=True,
)

# Pre-select the role the visitor is already using, but let them override it —
# someone browsing without a role set should still be able to identify themselves.
_role = current_role()
_role_index = ROLES.index(_role) if _role in ROLES else 0

with st.form("feedback_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        role = st.selectbox("I am a...", ROLES, index=_role_index)
    with c2:
        category = st.selectbox("What is this about?", CATEGORIES)

    rating = st.select_slider(
        "Overall, how would you rate this tool?",
        options=list(RATING_LABELS.keys()),
        value=4,
        format_func=lambda v: RATING_LABELS[v],
    )

    message = st.text_area(
        "Your feedback",
        placeholder=(
            "What worked well? What was confusing? What would make this more useful "
            "for you or the children you care for?"
        ),
        height=160,
    )

    contact = st.text_input(
        "Contact (optional)",
        help=(
            "Email or phone, only if you would like a reply. Leave blank to stay "
            "completely anonymous."
        ),
    )

    submitted = st.form_submit_button(
        "Submit feedback", type="primary", use_container_width=True
    )

if submitted:
    if not message.strip():
        st.error("Please write a little feedback before submitting.")
    else:
        try:
            db.save_feedback(
                role=role,
                rating=int(rating),
                category=category,
                message=message,
                contact=contact or None,
            )
        except Exception as exc:
            st.error(
                "Sorry - your feedback could not be saved "
                f"({type(exc).__name__}). Please try again."
            )
        else:
            st.success(
                "Thank you. Your feedback has been recorded - you can see it "
                "in the list below."
            )
            if contact.strip():
                st.caption("You left a contact, so we may follow up with you.")
            st.balloons()


# ---------------------------------------------------------------------------
# Public feed of what has been submitted.
#
# Deliberately does NOT render the `contact` column: a contact is given to the
# deployment owner for a private reply, not for publication. Clinicians see
# contacts on the dashboard; this page never does.
# ---------------------------------------------------------------------------

st.divider()

try:
    stats = db.feedback_stats()
    items = db.recent_feedback(limit=25)
except Exception as exc:
    st.caption(f"(Could not load feedback: {type(exc).__name__})")
    items, stats = [], None

if not items:
    st.markdown("### What people are saying")
    st.info("No feedback yet. Yours would be the first.")
else:
    st.markdown(f"### What people are saying ({stats['total']})")

    c1, c2 = st.columns(2)
    c1.metric("Total submissions", stats["total"])
    c2.metric(
        "Average rating",
        f"{stats['avg_rating']:.1f} / 5" if stats["avg_rating"] is not None else "-",
    )

    for f in items:
        stars = "★" * int(f["rating"] or 0) + "☆" * (5 - int(f["rating"] or 0))
        when = (f["submitted_at"] or "").replace("T", " ")
        # Escape the message: it is user-supplied and this card is raw HTML.
        safe_message = (
            (f["message"] or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        st.markdown(
            "<div class='info-card'>"
            f"<div style='display:flex; justify-content:space-between; align-items:baseline; gap:12px;'>"
            f"<b style='color:#1e3a8a;'>{f['role'] or 'Anonymous'}</b>"
            f"<span style='color:#b45309; letter-spacing:2px;'>{stars}</span>"
            f"</div>"
            f"<div style='color:#1c1917; margin:8px 0 6px 0;'>{safe_message}</div>"
            f"<div style='color:#78716c; font-size:12px;'>"
            f"{f['category'] or 'General'} &middot; {when}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
