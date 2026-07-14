"""About, ethics, and references.

Rebuilt from a single wall of prose into a scannable page: key figures up top,
then tabs so a reader can go straight to the section they came for. The content
is unchanged in substance -- this is the ethics page of a clinical tool, so it
stays sober. "Engaging" here means legible and well-structured, not jokey.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header  # noqa: E402

header()

NAVY = "#1e3a8a"
AMBER = "#b45309"
STONE = "#57534e"

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
        color:#fafaf9; padding:36px 40px 30px 40px; border-radius:6px;
        margin:6px 0 24px 0; border-bottom:3px solid #b45309;">
        <div style="font-size:11px; letter-spacing:0.18em; text-transform:uppercase;
                    opacity:0.75; margin-bottom:10px;">
            About &middot; Ethics &middot; Method
        </div>
        <h2 style="font-family:Georgia,'Times New Roman',serif; font-weight:700;
                   font-size:29px; line-height:1.2; margin:0 0 12px 0; color:#fafaf9;">
            How this tool works &mdash; and where it stops
        </h2>
        <div style="font-size:15px; opacity:0.88; line-height:1.6; max-width:640px;">
            A screening and referral support tool for the Nigerian pediatric
            population. It triages children before a clinical consultation. It
            does not, and cannot, diagnose one.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# The numbers
# ---------------------------------------------------------------------------
STATS = [
    ("37", "states covered", "all 36 + the FCT"),
    ("4&ndash;15", "years old", "the validated age range"),
    ("18", "DSM-5 symptoms", "9 inattention + 9 hyperactivity"),
    ("0", "names stored", "initials and a Study ID only"),
]

cols = st.columns(4, gap="small")
for col, (big, label, sub) in zip(cols, STATS):
    with col:
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #e7e5e4;
                        border-top:3px solid {NAVY}; border-radius:4px;
                        padding:18px 16px; text-align:center; height:130px;">
              <div style="font-family:Georgia,serif; font-size:30px; font-weight:700;
                          color:{NAVY}; line-height:1.1;">{big}</div>
              <div style="font-size:13px; font-weight:600; color:#44403c;
                          margin-top:6px;">{label}</div>
              <div style="font-size:11px; color:#78716c; margin-top:3px;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# The hard boundary -- deliberately the loudest thing on the page
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="border:2px solid #991b1b; background:#fef2f2; border-radius:6px;
                padding:20px 24px; margin-bottom:26px;">
      <div style="font-size:11px; letter-spacing:0.14em; text-transform:uppercase;
                  color:#991b1b; font-weight:700; margin-bottom:8px;">
        The line this tool does not cross
      </div>
      <div style="font-size:15px; color:#44403c; line-height:1.6;">
        <b>This is a screening tool, not a diagnostic one.</b> It assists
        overloaded pediatricians by triaging children before a full clinical
        consultation. A diagnosis of ADHD requires direct evaluation by a
        qualified child psychiatrist or pediatrician &mdash; and nothing shown
        anywhere in this app substitutes for that.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_risk, tab_form, tab_world, tab_bias, tab_privacy, tab_next, tab_refs = st.tabs([
    "How risk is scored",
    "The questionnaire",
    "What other countries do",
    "Ethics & bias",
    "Privacy",
    "What's next",
    "References",
])


# ---------------------------------------------------------------------------
with tab_risk:
    st.markdown("#### Three levels, one rule each")
    st.write(
        "A symptom counts as **endorsed** only when a rater marks it *Often* or "
        "*Very Often*. DSM-5 also requires that symptoms actually **impair** the "
        "child's functioning — which is why symptom count alone never reaches High Risk."
    )

    LEVELS = [
        ("Low Risk", "#166534", "#ecfdf5", "#bbf7d0",
         "Fewer than 3 endorsed symptoms.",
         "Healthy Development — standard guidance, no referral."),
        ("Moderate Risk", "#b45309", "#fffbeb", "#fde68a",
         "6+ symptoms but little impairment, <b>or</b> 3&ndash;5 symptoms.",
         "Watchful Monitoring — talk to teachers, check vision &amp; hearing, re-screen in 3&ndash;6 months."),
        ("High Risk", "#991b1b", "#fef2f2", "#fecaca",
         "6+ endorsed symptoms in a subscale <b>and</b> 2+ impaired performance areas.",
         "Immediate Referral — tertiary facilities listed, IEP recommended at school."),
    ]
    for name, colour, bg, border, rule, action in LEVELS:
        st.markdown(
            f"""
            <div style="background:{bg}; border:1px solid {border};
                        border-left:5px solid {colour}; border-radius:4px;
                        padding:14px 18px; margin-bottom:10px;">
              <div style="color:{colour}; font-weight:700; font-size:14px;
                          letter-spacing:0.03em;">{name}</div>
              <div style="color:#44403c; font-size:14px; margin-top:5px;">
                <b>Rule:</b> {rule}</div>
              <div style="color:{STONE}; font-size:13px; margin-top:4px;">
                <b>Then:</b> {action}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "**Why referrals are gated to High Risk.** Specialist child-psychiatry "
        "appointments in Nigeria are scarce. Sending a low-risk child both alarms "
        "the family and takes a slot from a child who needs it."
    )


# ---------------------------------------------------------------------------
with tab_form:
    st.markdown("#### Adapted from the NICHQ Vanderbilt Assessment Scale")
    st.write(
        "Public domain, DSM-aligned, and adapted here for the Nigerian context. "
        "Two parallel forms, so the same child can be rated at home *and* at school."
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(
            f"""
            <div class='info-card' style='border-left-color:{NAVY};'>
              <b style='color:{NAVY};'>👪 Parent / Caregiver — 47 items</b>
              <ul style='margin:8px 0 0 -12px; color:#44403c; font-size:14px; line-height:1.7;'>
                <li>18 DSM-5 core symptoms</li>
                <li>8 home &amp; academic performance items</li>
                <li>4 oppositional-defiant screening items</li>
                <li>3 anxiety / mood items</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class='info-card' style='border-left-color:#7c2d12;'>
              <b style='color:#7c2d12;'>🏫 Teacher — 35 items</b>
              <ul style='margin:8px 0 0 -12px; color:#44403c; font-size:14px; line-height:1.7;'>
                <li>the same 18 DSM-5 core symptoms</li>
                <li>8 classroom-context performance items</li>
                <li>the same brief comorbidity screens</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Why ask two people about one child?")
    st.write(
        "Because ADHD frequently presents in only one setting. A child may cope "
        "in a quiet home and struggle in a class of forty — or the reverse. The "
        "tool scores both raters, reports their agreement, and lets the **higher** "
        "rating drive the referral decision. Disagreement is a finding, not an error."
    )


# ---------------------------------------------------------------------------
with tab_world:
    st.markdown("#### What we borrowed, and from where")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(
            """
            <div class='info-card'>
              <b>🇺🇸 United States</b>
              <p style='color:#44403c; font-size:14px; margin-top:8px;'>
                The Vanderbilt scale is used by roughly <b>80% of US pediatricians</b>
                — because it is free, public domain, DSM-aligned, and has parallel
                parent and teacher forms. Conners 3 is the proprietary alternative;
                it emphasises multi-informant agreement.
              </p>
              <p style='color:#57534e; font-size:13px; margin-bottom:0;'>
                <b>We took:</b> parallel forms + cross-informant agreement,
                without the proprietary licence fee.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class='info-card' style='border-left-color:#7c2d12;'>
              <b>🇨🇳 China</b>
              <p style='color:#44403c; font-size:14px; margin-top:8px;'>
                Validated Chinese SNAP-IV and CBCL drive most tertiary-hospital
                screening, and WeChat mini-programs let parents complete a screen
                and be <b>auto-routed to the nearest children's hospital</b> with a
                child psychiatry unit.
              </p>
              <p style='color:#57534e; font-size:13px; margin-bottom:0;'>
                <b>We took:</b> the auto-routing model — mapped onto Nigeria's
                Federal Neuro-Psychiatric, Federal Teaching, and State Teaching
                hospitals, by state of residence.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class='info-card' style='border-left-color:{AMBER};'>
          <b>🇳🇬 Nigeria — what is different here</b>
          <p style='color:#44403c; font-size:14px; margin-top:8px; margin-bottom:0;'>
            Built for all 36 states and the FCT. <b>Offline-first</b>, because
            power and connectivity are not guaranteed: SQLite storage, the model
            runs on-device, and a screening can be completed with no internet at
            all.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
with tab_bias:
    st.markdown("#### The bias we went looking for")
    st.markdown(
        f"""
        <div class='info-card' style='border-left-color:{AMBER};'>
          <b>Girls with ADHD are under-diagnosed.</b>
          <p style='color:#44403c; font-size:14px; margin-top:8px; margin-bottom:0;'>
            ADHD prevalence is traditionally reported higher in boys — but a
            growing body of evidence shows that <b>inattentive-type ADHD in girls
            is missed</b>, because girls tend to present with quiet
            distractibility rather than disruptive hyperactivity. A model trained
            naively on historical data would inherit that blind spot and keep
            missing them.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "So the training data is **deliberately synthesised to give girls slightly "
        "higher inattention base rates**, so the model does not learn to overlook them."
    )

    st.markdown("#### The machine never gets the last word")
    st.write(
        "The rule-based DSM-5 score is **always shown next to** the ML prediction. "
        "If the two disagree, **the rule-based result is authoritative** — the ML "
        "score is a calibration aid, not a black-box override. A clinician can see "
        "the reasoning instead of being handed an unexplained verdict."
    )


# ---------------------------------------------------------------------------
with tab_privacy:
    st.markdown("#### What we store, and what we refuse to")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown(
            """
            <div class='info-card' style='border-left-color:#166534;'>
              <b style='color:#166534;'>✓ &nbsp;Stored</b>
              <ul style='margin:8px 0 0 -12px; color:#44403c; font-size:14px; line-height:1.7;'>
                <li>First and last <b>initial</b> only</li>
                <li>An opaque Study ID (<code>ADHD-NG-XXXXXX</code>)</li>
                <li>Age, gender, school level, state</li>
                <li>The questionnaire responses</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class='info-card' style='border-left-color:#991b1b;'>
              <b style='color:#991b1b;'>✗ &nbsp;Never stored</b>
              <ul style='margin:8px 0 0 -12px; color:#44403c; font-size:14px; line-height:1.7;'>
                <li>The child's <b>name</b></li>
                <li>Any cloud sync or backup</li>
                <li>Third-party analytics or telemetry</li>
                <li>Anything sent off the device</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write(
        "All data sits in a local SQLite database. The trained Random Forest and "
        "its metadata are small `.joblib` artifacts — the whole payload is light "
        "enough for a low-spec Android device. Screening works in clinics with "
        "intermittent power and no connectivity."
    )


# ---------------------------------------------------------------------------
with tab_next:
    st.markdown("#### Scaling roadmap")
    ROADMAP = [
        ("Translations", "Yoruba, Igbo and Hausa. The i18n scaffold is already in "
                         "place — only the translation strings are missing."),
        ("Offline mobile PWA", "Wrap the app into an installable PWA so primary "
                               "health workers can screen from their own phones."),
        ("Referral confirmation loop", "Hospitals confirm the appointment back "
                                       "against the Study ID, so the dashboard can "
                                       "track the funnel from screening → specialist "
                                       "→ diagnosis."),
        ("Anonymised research export", "One-click CSV of all sessions — "
                                       "demographics and risk levels, no PII — for "
                                       "academic research under IRB approval."),
        ("Model recalibration", "Once real Nigerian-population data exists, retrain "
                                "without touching the rest of the pipeline. The "
                                "rule-based scorer stays the safety net."),
    ]
    for i, (title, body) in enumerate(ROADMAP, start=1):
        st.markdown(
            f"""
            <div style="display:flex; gap:16px; align-items:flex-start;
                        padding:14px 0; border-bottom:1px solid #e7e5e4;">
              <div style="flex:0 0 34px; height:34px; border-radius:50%;
                          background:{NAVY}; color:#fafaf9; font-weight:700;
                          display:flex; align-items:center; justify-content:center;
                          font-size:14px;">{i}</div>
              <div>
                <div style="font-weight:700; color:{NAVY}; font-size:15px;">{title}</div>
                <div style="color:#44403c; font-size:14px; margin-top:3px;">{body}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
with tab_refs:
    st.markdown("#### References")
    st.markdown(
        """
        - American Academy of Pediatrics. *Clinical Practice Guideline for the
          Diagnosis, Evaluation, and Treatment of ADHD in Children and Adolescents.*
        - Wolraich ML et al. *NICHQ Vanderbilt Assessment Scale.* American Academy
          of Pediatrics & National Initiative for Children's Healthcare Quality.
        - American Psychiatric Association. *DSM-5* — Attention-Deficit/Hyperactivity
          Disorder diagnostic criteria.
        - Su YE et al. *Validation of the Chinese SNAP-IV.*
        - Federal Ministry of Health, Nigeria. *Mental Health Service Delivery
          Framework.*
        """
    )
    st.caption(
        "Hospital directory compiled from the Federal Ministry of Health hospital "
        "register and the MDCN accredited teaching-hospital list. Phone numbers are "
        "deliberately omitted — they change often, and wrong clinical contact "
        "details are dangerous."
    )
