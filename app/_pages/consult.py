"""
Consult a Clinician -- COMING SOON placeholder.

The full paid-consultation implementation (Paystack checkout, server-side
payment verification, and the live 2-second-refresh chat thread) is complete and
tested. It lives in `_consult_paid_flow.py` and is deliberately NOT registered
in streamlit_app.py, so nothing loads it.

To turn the real feature on:
    1. Put Paystack keys in .streamlit/secrets.toml under [paystack].
    2. Move consultations off SQLite -- Streamlit Cloud wipes the filesystem on
       every redeploy, which would destroy consultations people paid for.
    3. In streamlit_app.py, point consult_pg at "_pages/_consult_paid_flow.py".
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header  # noqa: E402

header("Consult a Clinician")

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
        color: #fafaf9;
        padding: 46px 44px;
        border-radius: 6px;
        margin: 8px 0 26px 0;
        border-bottom: 3px solid #b45309;
        text-align: center;
    ">
        <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase;
                    opacity:0.75; margin-bottom:12px;">
            Coming Soon
        </div>
        <h2 style="font-family:Georgia,'Times New Roman',serif; font-weight:700;
                   font-size:30px; line-height:1.2; margin:0 0 14px 0; color:#fafaf9;">
            Talk directly with a clinician
        </h2>
        <div style="font-size:15px; opacity:0.88; line-height:1.6;
                    max-width:560px; margin:0 auto;">
            We are building a private consultation service where you can discuss
            your child's screening result with a verified clinician and get help
            deciding what to do next.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    st.markdown(
        "<div class='role-card' style='height:auto;'>"
        "<h4>Private</h4>"
        "<p>A one-to-one conversation about your result &mdash; not a public forum.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        "<div class='role-card' style='height:auto; border-top-color:#7c2d12;'>"
        "<h4 style='color:#7c2d12;'>Verified</h4>"
        "<p>You speak with a clinician the deployment owner has verified, not a bot.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        "<div class='role-card' style='height:auto; border-top-color:#166534;'>"
        "<h4 style='color:#166534;'>Result-aware</h4>"
        "<p>Share your Study ID so the clinician can see the screening you are asking about.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)

st.markdown("#### In the meantime")
st.markdown(
    """
    - **If your result was High Risk**, your result page lists the tertiary
      facilities nearest to you. Download the PDF report and take it with you.
    - **If your result was Moderate Risk**, speak to your child's teachers, rule
      out vision and hearing problems, and re-screen in 3-6 months.
    - **Questions about the result itself?** The **FAQ** page answers the most
      common ones.
    - **Want to be told when consultations open?** Leave a note on the
      **Feedback** page with your contact details.
    """
)

st.divider()
st.warning(
    "**A consultation will never be a diagnosis.** ADHD diagnosis requires "
    "direct evaluation by a qualified child psychiatrist or pediatrician. If "
    "your child is in crisis, go to a hospital now &mdash; do not wait for this "
    "service."
)
