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
            "Both the number of symptoms and their impact on daily life meet the "
            "threshold for specialist review. Book an appointment at one of the "
            "facilities below. This is a screening result, not a diagnosis -- the "
            "specialist makes the final decision."
        ),
        "actions": [
            "Book the Child Psychiatry / Child & Adolescent Mental Health clinic at "
            "the closest facility listed below.",
            "Ask the school about an Individualized Education Program (IEP) or "
            "classroom adjustments.",
        ],
        "help_headline": "Ways to help your child day-to-day while you arrange specialist care",
        "help_strategies": [
            "Keep a very predictable daily routine -- steady times for waking, "
            "homework, meals, and sleep. Predictability lowers overwhelm.",
            "Give one small instruction at a time and check in after each step, "
            "rather than several instructions at once.",
            "Create a quiet, tidy space for focused work, with phones and TV off.",
            "Notice and praise effort and small wins straight away -- this works "
            "better than punishing mistakes.",
            "Build in short movement breaks and daily physical activity to release "
            "energy.",
            "Protect sleep and keep screen time low, especially before bed.",
        ],
    },
    MODERATE: {
        "headline": "Watchful Monitoring",
        "summary": (
            "A few signs are showing, but not enough to point to ADHD right now. "
            "This is common -- many children show some of these behaviours as they "
            "grow. The right step is to watch closely and act early if they persist, "
            "not to worry."
        ),
        "watch_for": [
            "Trouble staying focused on schoolwork or play",
            "Restlessness or constant fidgeting",
            "Not finishing tasks or chores",
            "Acting or speaking without thinking first",
            "Forgetting or losing things needed for daily tasks",
            "Difficulty following instructions that have several steps",
        ],
        "help_headline": "Ways to help now (and lower the chance it grows)",
        "help_strategies": [
            "Add structure: a simple visual daily routine the child can see and follow.",
            "Break homework into short, timed chunks with a break in between.",
            "Set one or two clear house rules and follow through calmly and "
            "consistently.",
            "Use a small reward chart for focus and finishing tasks -- reward effort, "
            "not perfection.",
            "Work with the teacher so home and school use the same approach.",
            "Protect sleep and steady meals, keep daily play or exercise, and cut "
            "distractions during focus time.",
        ],
    },
    LOW: {
        "headline": "No Strong Signs -- Healthy Range",
        "summary": (
            "This screening found no strong signs of ADHD. Your child's behaviour "
            "falls within the normal range for their age. There is nothing to worry "
            "about right now."
        ),
        "watch_for": [
            "A teacher raising a new concern about focus or behaviour",
            "A clear, lasting change in attention, activity level, or mood",
            "New trouble finishing schoolwork or following daily routines",
        ],
        "help_headline": "Ways to keep supporting healthy development",
        "help_strategies": [
            "Keep consistent routines for sleep, meals, homework, and play.",
            "Protect enough sleep for their age and keep screen time limited and "
            "balanced.",
            "Give plenty of chances to read, play, and finish small tasks -- this "
            "builds focus and self-control.",
            "Praise effort and patience so good habits stick.",
            "Stay in regular touch with the teacher so any change is caught early.",
        ],
    },
}

# Recommended re-check WINDOW (earliest, latest) in months from the screening
# date. Low is checked less often; Moderate sooner (it is closer to threshold).
# High Risk goes straight to specialist referral, so it has no self re-check
# window -- waiting would only delay care.
FOLLOW_UP_WINDOW: dict[str, tuple[int, int] | None] = {
    HIGH: None,
    MODERATE: (2, 3),
    LOW: (4, 6),
}


def shows_referrals(risk_level: str) -> bool:
    """True only for the risk levels that warrant a tertiary hospital referral."""
    return risk_level in REFERRAL_RISK_LEVELS


def guidance_for(risk_level: str) -> dict:
    """Headline / summary / action bullets for a risk level. Falls back to Moderate
    for an unrecognised level so the family is never left with no advice."""
    return GUIDANCE.get(risk_level, GUIDANCE[MODERATE])


def follow_up_window(risk_level: str) -> tuple[int, int] | None:
    """The recommended re-check window (earliest, latest months from today), or
    None when immediate referral (High Risk) makes a self re-check inappropriate."""
    return FOLLOW_UP_WINDOW.get(risk_level)


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
