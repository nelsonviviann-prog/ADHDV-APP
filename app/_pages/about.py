"""About, ethics, and references page."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header

header("About & Ethics")

st.markdown("## Clinical scoping")
st.markdown(
    """
This is a **screening and referral support tool**, not an automated diagnostic
tool. It assists overloaded pediatricians by triaging children before full
clinical consultations. Every result reinforces that diagnosis requires direct
evaluation by a qualified child psychiatrist or pediatrician.
    """
)

st.markdown("## Instrument design")
st.markdown(
    """
The questionnaire adapts the **NICHQ Vanderbilt Assessment Scale** (public
domain, USA) to the Nigerian context. Two parallel forms:

- **Parent / Caregiver form** - 47 items: 18 DSM-5 core symptoms (9 inattention
  + 9 hyperactivity/impulsivity), 8 home and academic performance items,
  4 oppositional-defiant screening items, 3 anxiety / mood items.
- **Teacher form** - 35 items: same 18 DSM-5 core items, 8 classroom-context
  performance items, plus the same brief comorbidity screens.

Risk thresholds follow DSM-5:
- High Risk: >= 6 endorsed symptoms in either subscale AND >= 2 impaired
  performance areas.
- Moderate Risk: >= 6 endorsed symptoms without functional impairment, OR
  3-5 subthreshold symptoms.
- Low Risk: < 3 endorsed symptoms.
    """
)

st.markdown("## What we learned from systems in other countries")
st.markdown(
    """
**United States.** The Vanderbilt scale is used by ~80% of US pediatricians
specifically because it is free, public domain, DSM-aligned, and has parallel
parent and teacher forms. Conners 3 is the proprietary alternative; it
emphasises **multi-informant agreement** and self-report for children >= 8.
We borrow both ideas (parallel forms + cross-informant agreement) without
the proprietary cost.

**China.** Validated Chinese versions of SNAP-IV and the CBCL drive most
tertiary-hospital screening, and a growing number of WeChat mini-programs
let parents complete a screen and be auto-routed to the nearest children's
hospital with a child psychiatry unit. We replicate the auto-routing model
- mapping screening results to the nearest Nigerian Federal Neuro-Psychiatric
Hospital, Federal Teaching Hospital, or State Teaching Hospital, per the
patient's state of residence.
    """
)

st.markdown("## Ethical AI & bias")
st.markdown(
    """
ADHD prevalence is traditionally higher in boys than girls, but a growing
body of evidence shows that **inattentive-type ADHD in girls is
under-diagnosed** because girls present with quiet distractibility rather
than disruptive hyperactivity. The training data is intentionally synthesised
to give girls slightly higher inattention base rates so the model does not
inherit the historical under-detection bias.

The rule-based DSM-5 score is always shown alongside the ML prediction. If
the two disagree, the rule-based result is authoritative; the ML score is a
calibration aid, not a black-box override.

No personally-identifying information leaves the device. Children are tracked
by a short opaque Study ID (`ADHD-NG-XXXXXX`); only initials are stored.
    """
)

st.markdown("## Data & privacy architecture")
st.markdown(
    """
- All data sits in a local SQLite database (`data/screening_sessions.db`).
- The trained Random Forest model and metadata are bundled as `.joblib`
  artifacts in `models/`. Total payload is small enough to install on
  low-spec Android devices via a packaged PWA (a future deployment target).
- No cloud sync, no third-party analytics, no telemetry. The screening can
  be completed entirely offline in clinics with intermittent power /
  connectivity.
    """
)

st.markdown("## Scaling roadmap")
st.markdown(
    """
1. **Translations** - Yoruba, Igbo, and Hausa. The i18n scaffold is in place;
   only translation strings need to be added.
2. **Offline mobile PWA** - wrap Streamlit (or a lightweight Flask front-end)
   into an installable PWA so primary health workers can run screenings on
   their own phones.
3. **Referral confirmation loop** - hospitals confirm appointment booking
   back to the parent's Study ID; the dashboard tracks the funnel from
   screening to specialist appointment to diagnosis.
4. **Anonymised research export** - one-click CSV of all sessions, with
   demographics and risk levels but no PII, for academic research with IRB
   approval.
5. **Model recalibration** - once real Nigerian-population data is collected,
   the model can be retrained without changing the rest of the pipeline
   (the rule-based scorer stays the safety net).
    """
)

st.markdown("## References")
st.markdown(
    """
- American Academy of Pediatrics. *Clinical Practice Guideline for the
  Diagnosis, Evaluation, and Treatment of ADHD in Children and Adolescents.*
- Wolraich ML et al. *NICHQ Vanderbilt Assessment Scale.* American Academy
  of Pediatrics & National Initiative for Children's Healthcare Quality.
- American Psychiatric Association. *DSM-5* - Attention-Deficit/Hyperactivity
  Disorder diagnostic criteria.
- Su YE et al. *Validation of the Chinese SNAP-IV.* (Chinese
  pediatric-population validation work.)
- Federal Ministry of Health, Nigeria. *Mental Health Service Delivery
  Framework.*
    """
)
