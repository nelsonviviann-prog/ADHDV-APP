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
            "Some symptoms are present but do not currently meet the threshold "
            "for immediate specialist referral. Monitor and re-screen."
        ),
        "actions": [
            "Consult with school teachers to monitor focus across classroom settings.",
            "Recommend a physical assessment (vision & hearing) to rule out sensory delays.",
            "Schedule a follow-up screening questionnaire in 3-6 months.",
        ],
    },
    LOW: {
        "headline": "Healthy Development",
        "summary": (
            "Symptom load falls within the expected bounds of standard pediatric "
            "development."
        ),
        "actions": [
            "Provide standard healthy lifestyle and focus-behaviour guidance.",
            "Re-screen only if new concerns arise at home or at school.",
        ],
    },
}


def shows_referrals(risk_level: str) -> bool:
    """True only for the risk levels that warrant a tertiary hospital referral."""
    return risk_level in REFERRAL_RISK_LEVELS


def guidance_for(risk_level: str) -> dict:
    """Headline / summary / action bullets for a risk level. Falls back to Moderate
    for an unrecognised level so the family is never left with no advice."""
    return GUIDANCE.get(risk_level, GUIDANCE[MODERATE])


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
