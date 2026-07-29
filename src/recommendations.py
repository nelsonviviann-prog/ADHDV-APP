"""
What to tell the family, per risk level.

Referrals to tertiary hospitals are shown for HIGH RISK ONLY. Sending a
low-risk family to a Federal Neuro-Psychiatric Hospital is both alarming and
a waste of a scarce specialist appointment, so Moderate and Low instead get
actionable monitoring / developmental guidance.

Risk levels come from src.scoring (DSM-5 symptom counts + impairment count),
NOT from a raw numeric total.
"""

from __future__ import annotations

from .hospitals import Hospital, referral_recommendations

HIGH = "High Risk"
MODERATE = "Moderate Risk"
LOW = "Low Risk"

# Only High Risk gets hospital referrals.
REFERRAL_RISK_LEVELS = (HIGH,)

# National tertiary centres with established child & adolescent mental health
# units. Always offered at High Risk in addition to the state-routed list, so a
# family always has a known-good option even if their state has thin provision.
NATIONAL_CENTRE_ABBRS = ("LUTH", "UCH", "FNPHY")

GUIDANCE: dict[str, dict] = {
    HIGH: {
        "headline": "Immediate Referral",
        "summary": (
            "Symptoms and functional impairment both meet the threshold for "
            "specialist review. Book an appointment at one of the facilities below."
        ),
        "actions": [
            "Child Psychiatry Clinic at the closest regional State Teaching Hospital.",
            "School Action: recommend IEP (Individualized Education Program) adjustments.",
        ],
    },
    MODERATE: {
        "headline": "Watchful Monitoring",
        "summary": (
            "A few signs are showing, but not enough to point to ADHD right now. "
            "This is common -- many children show some of these behaviours as they "
            "grow. The right step now is to watch closely, not to worry."
        ),
        "actions": [
            "Over the next 3 months, watch for these specific behaviours: trouble "
            "staying focused on schoolwork or play, restlessness or constant "
            "fidgeting, not finishing tasks or chores, and acting or speaking "
            "without thinking first.",
            "Keep a short weekly note of when these happen and where -- at home, at "
            "school, or both. A pattern across settings matters more than one-off days.",
            "Ask your child's teacher whether they notice the same behaviours in "
            "class. A child can struggle in one setting and cope in another.",
            "Rule out simple causes first: book a basic vision and hearing check, and "
            "keep sleep, meals, and screen time steady.",
            "Re-screen in 3 months. If the same behaviours are still there -- or have "
            "grown -- that is your signal to seek a specialist assessment. If they "
            "have eased, no further action is needed.",
        ],
    },
    LOW: {
        "headline": "No Strong Signs -- Healthy Range",
        "summary": (
            "This screening found no strong signs of ADHD. Your child's behaviour "
            "falls within the normal range for their age. There is nothing to worry "
            "about right now."
        ),
        "actions": [
            "No special action is needed. Keep supporting focus and self-control the "
            "everyday way: consistent routines, enough sleep, limited screen time, "
            "and plenty of space to play, read, and finish small tasks.",
            "You do not need to re-screen on a fixed schedule. Re-screen if something "
            "new comes up -- a teacher raises a concern, or you notice a clear change "
            "in focus, activity, or behaviour at home.",
            "For peace of mind, you can set an optional 3-month reminder below to "
            "re-check how things are going.",
        ],
    },
}

# Months until a recommended re-screen, per risk level. High Risk goes straight
# to specialist referral, so a scheduled self re-screen would only delay care --
# hence None.
FOLLOW_UP_MONTHS: dict[str, int | None] = {HIGH: None, MODERATE: 3, LOW: 3}


def shows_referrals(risk_level: str) -> bool:
    """True only for the risk levels that warrant a tertiary hospital referral."""
    return risk_level in REFERRAL_RISK_LEVELS


def guidance_for(risk_level: str) -> dict:
    """Headline / summary / action bullets for a risk level. Falls back to Moderate
    for an unrecognised level so the family is never left with no advice."""
    return GUIDANCE.get(risk_level, GUIDANCE[MODERATE])


def follow_up_months(risk_level: str) -> int | None:
    """Months until a recommended re-screen, or None when immediate referral
    (High Risk) makes a scheduled self re-screen inappropriate."""
    return FOLLOW_UP_MONTHS.get(risk_level)


def national_centres() -> list[Hospital]:
    """The always-offered national tertiary centres, in the declared order."""
    from .hospitals import HOSPITALS

    by_abbr = {h.abbreviation: h for h in HOSPITALS}
    return [by_abbr[a] for a in NATIONAL_CENTRE_ABBRS if a in by_abbr]


def referrals_for(state: str) -> list[Hospital]:
    """State-routed facilities plus the national centres, de-duplicated.

    A family in Lagos would otherwise see LUTH twice (once from state routing,
    once as a national centre), so the state list wins and national centres only
    fill in what is missing.
    """
    local = referral_recommendations(state) or []
    seen = {h.abbreviation for h in local}
    return local + [h for h in national_centres() if h.abbreviation not in seen]


def overall_risk(*results) -> str | None:
    """The most severe risk level across the given ScreeningResults.

    A child is referred if EITHER rater flags High Risk -- ADHD frequently
    presents in only one setting, so taking the max (not the average) is the
    clinically safe direction to err in.
    """
    order = {LOW: 0, MODERATE: 1, HIGH: 2}
    levels = [r.risk_level for r in results if r is not None]
    if not levels:
        return None
    return max(levels, key=lambda lvl: order.get(lvl, 0))
