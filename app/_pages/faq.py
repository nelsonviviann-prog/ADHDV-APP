"""
Frequently asked questions - open to everyone, no role required.

Content is deliberately consistent with what the tool actually does: the
thresholds quoted here mirror src/scoring.py and src/recommendations.py. If the
scoring rules change, change these answers too.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header  # noqa: E402

header("Frequently Asked Questions")

st.markdown(
    "<div class='info-card'>"
    "<b>Short answers to the questions parents, teachers, and health workers "
    "ask most.</b><br>"
    "<span style='color:#57534e;'>Still stuck? Leave a note on the "
    "<b>Feedback</b> page and we will get back to you.</span>"
    "</div>",
    unsafe_allow_html=True,
)

FAQS: list[tuple[str, str]] = [
    # ---- The big one, first ----
    (
        "Does this tool diagnose my child with ADHD?",
        """
**No. It cannot, and it is not designed to.**

This is a *screening* tool. It tells you whether a child's reported behaviour
looks like it warrants a professional assessment. Only a qualified child
psychiatrist or pediatrician can diagnose ADHD, and they do so through direct
evaluation of the child, developmental history, and observation across settings
- not from a questionnaire.

A "High Risk" result does **not** mean your child has ADHD. A "Low Risk" result
does **not** rule it out. If you are worried about your child, speak to a
doctor regardless of what this screening says.
        """,
    ),
    (
        "How is the risk level calculated?",
        """
The tool follows **DSM-5** criteria. A symptom counts as "endorsed" when it is
rated *Often* or *Very Often*. It then applies these rules:

- **High Risk** - 6 or more endorsed symptoms in either the inattention or the
  hyperactivity/impulsivity list, **and** 2 or more areas of impaired
  performance (school, reading, writing, maths, relationships, activities).
- **Moderate Risk** - 6 or more endorsed symptoms but little functional
  impairment, **or** 3 to 5 symptoms.
- **Low Risk** - fewer than 3 endorsed symptoms.

Note that symptoms alone are not enough for High Risk. DSM-5 requires that the
symptoms actually *interfere with the child's functioning*, which is why
impairment is part of the rule.
        """,
    ),
    (
        "Why didn't I get a hospital referral?",
        """
Hospital referrals are shown for **High Risk results only**.

This is deliberate. Specialist child psychiatry appointments in Nigeria are
scarce, and sending a child who does not need one is both alarming for the
family and takes a slot from a child who does.

At **Moderate Risk** you get a monitoring plan instead: talk to the child's
teachers, rule out vision and hearing problems, and re-screen in 3-6 months.
At **Low Risk** you get standard healthy-development guidance. In both cases,
if your own concern persists, see your pediatrician - the screening does not
overrule a parent's judgement.
        """,
    ),
    (
        "The parent and teacher results disagree. Which one is right?",
        """
**Both, usually.** This is one of the most clinically useful things the tool
surfaces, not an error.

ADHD often presents differently at home and at school. A child may cope in a
quiet home and struggle in a class of 40, or the reverse. That is why the tool
asks both raters and reports a cross-informant agreement.

When ratings disagree, the **higher** rating should drive the referral
decision. A child flagged High by only one rater is still referred.
        """,
    ),
    (
        "What is a Study ID and why do I need it?",
        """
A Study ID (like `ADHD-NG-4F2A9C`) is a short, anonymous code that links a
parent's rating and a teacher's rating for the *same child* - without ever
storing the child's name.

When you complete a screening you are given one. Share it with the child's
teacher (or with the parent, if you are the teacher) so they can enter it and
add their view. Only then can the tool compare both perspectives.

Keep it - you also need it to add a follow-up screening later.
        """,
    ),
    (
        "Is my child's information private?",
        """
Yes. This is a core design constraint, not an afterthought.

- The child's **name is never stored** - only their first and last initial.
- Children are tracked by an anonymous Study ID.
- All data stays in a local database on the device running the tool. There is
  no cloud sync, no third-party analytics, and no telemetry.
- Feedback you leave is anonymous, and any contact details you volunteer are
  shown only to the deployment owner, never published.
        """,
    ),
    (
        "What ages is this for?",
        """
**Ages 4 to 15.** The questionnaire and the model are built around this range.

Below 4, ADHD-type behaviours are extremely difficult to distinguish from
ordinary toddler development. Above 15, adolescent and adult instruments are
more appropriate.
        """,
    ),
    (
        "What does the 'ML model risk' mean, and what if it disagrees with the DSM-5 result?",
        """
Alongside the DSM-5 rule-based score, a Random Forest model trained on the
project dataset gives a second opinion. You see both.

**If they disagree, the rule-based DSM-5 result is authoritative.** The ML
score is a calibration aid, not a black-box override. Showing both is
intentional: a clinician can see the reasoning rather than being handed an
unexplained verdict.
        """,
    ),
    (
        "How long does the screening take?",
        """
About **10 to 15 minutes**. The parent form has 47 items and the teacher form
35, but most are quick behavioural ratings on a five-point scale.

Answer for the child's behaviour **over the last 6 months**, not just this
week. A bad fortnight is not ADHD.
        """,
    ),
    (
        "Can I re-take the screening later?",
        """
Yes, and at Moderate Risk you are explicitly advised to - **in 3 to 6 months**.

Enter the same **Study ID** when you screen again. The tool keeps the history,
so a clinician can see whether things are improving, stable, or worsening over
time. That trajectory is often more informative than any single result.
        """,
    ),
    (
        "Who can see the Clinician Dashboard?",
        """
Only verified clinicians. Access requires a personal code issued by the
deployment owner, and every action a clinician takes - signing in, opening a
Study ID, viewing the dashboard - is written to an audit log tagged with their
name.

Parents and teachers never see other families' data.
        """,
    ),
    (
        "My child scored High Risk. What do I do now?",
        """
1. **Don't panic.** This is a screening flag, not a diagnosis.
2. **Download the PDF report** from the results page.
3. **Book an appointment** at one of the facilities listed in your result -
   your state's tertiary hospital, or one of the national centres (LUTH in
   Lagos, UCH in Ibadan, or the Federal Neuro-Psychiatric Hospital, Yaba).
4. **Take the report with you.** It saves the clinician time and gives them
   the parent and teacher ratings in one place.
5. **Talk to the school** about IEP (Individualized Education Program)
   adjustments while you wait for the appointment.
        """,
    ),
]

for question, answer in FAQS:
    with st.expander(question, expanded=False):
        st.markdown(answer)

st.divider()
st.info(
    "**Reminder:** this tool provides screening results only - never a "
    "diagnosis. If you are concerned about your child, consult a qualified "
    "child psychiatrist or pediatrician regardless of the result shown here."
)
