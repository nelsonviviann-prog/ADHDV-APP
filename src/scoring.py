"""
DSM-5 aligned scoring for the Vanderbilt-style ADHD screening form.

Outputs:
    presentation     -- 'Predominantly Inattentive', 'Predominantly Hyperactive-Impulsive',
                        'Combined', or 'Subthreshold'.
    risk_level       -- 'Low Risk' | 'Moderate Risk' | 'High Risk'.
    impairment_count -- number of performance areas rated 4 or 5.
    flags            -- list of dicts with comorbidity flags (ODD, anxiety/mood).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import config as cfg


@dataclass
class ScreeningResult:
    inattention_endorsed: int
    hyperactivity_endorsed: int
    inattention_total: int
    hyperactivity_total: int
    presentation: str
    impairment_count: int
    impaired_areas: list[str]
    risk_level: str
    rule_based_risk_code: int
    flags: list[dict] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)

    @property
    def core_total(self) -> int:
        return self.inattention_total + self.hyperactivity_total


def _count_endorsed(responses: dict, items: list[str]) -> int:
    return sum(1 for k in items if int(responses.get(k, 0)) >= cfg.ENDORSEMENT_THRESHOLD)


def _sum_items(responses: dict, items: list[str]) -> int:
    return sum(int(responses.get(k, 0)) for k in items)


def _presentation(inatt: int, hi: int) -> str:
    meets_inatt = inatt >= cfg.DSM5_SYMPTOM_THRESHOLD
    meets_hi = hi >= cfg.DSM5_SYMPTOM_THRESHOLD
    if meets_inatt and meets_hi:
        return "Combined Presentation"
    if meets_inatt:
        return "Predominantly Inattentive Presentation"
    if meets_hi:
        return "Predominantly Hyperactive-Impulsive Presentation"
    return "Subthreshold (does not meet DSM-5 symptom count)"


def _risk_level(
    inatt_endorsed: int,
    hi_endorsed: int,
    impairment_count: int,
) -> tuple[str, list[str]]:
    explanation: list[str] = []
    max_endorsed = max(inatt_endorsed, hi_endorsed)

    if (
        max_endorsed >= cfg.REFERRAL_THRESHOLDS["high_min_symptom_count"]
        and impairment_count >= cfg.REFERRAL_THRESHOLDS["high_min_impairment_count"]
    ):
        explanation.append(
            f"{max_endorsed} symptoms endorsed (>= {cfg.DSM5_SYMPTOM_THRESHOLD} DSM-5 threshold)"
        )
        explanation.append(
            f"{impairment_count} performance areas impaired "
            f"(>= {cfg.REFERRAL_THRESHOLDS['high_min_impairment_count']} required for HIGH)"
        )
        return "High Risk", explanation

    if max_endorsed >= cfg.REFERRAL_THRESHOLDS["high_min_symptom_count"]:
        explanation.append(
            f"{max_endorsed} symptoms endorsed but only {impairment_count} performance "
            f"area(s) impaired -- screened down to MODERATE."
        )
        return "Moderate Risk", explanation

    if max_endorsed >= cfg.REFERRAL_THRESHOLDS["moderate_min_symptom_count"]:
        explanation.append(
            f"{max_endorsed} symptoms endorsed (subthreshold) with "
            f"{impairment_count} impaired performance area(s)."
        )
        return "Moderate Risk", explanation

    explanation.append(
        f"Only {max_endorsed} symptoms endorsed -- below screening threshold."
    )
    return "Low Risk", explanation


def _impairment(responses: dict) -> tuple[int, list[str]]:
    impaired: list[str] = []
    for k in cfg.PERFORMANCE_ITEMS:
        rating = int(responses.get(k, 3))
        if rating >= 4:
            impaired.append(k)
    return len(impaired), impaired


def _comorbidity_flags(responses: dict) -> list[dict]:
    flags: list[dict] = []

    odd_endorsed = _count_endorsed(responses, cfg.ODD_ITEMS)
    if odd_endorsed >= 4:
        flags.append({
            "domain": "Oppositional Defiant",
            "severity": "High",
            "message": "Co-occurring Oppositional Defiant Disorder symptoms screen positive. "
                       "Add behavioural assessment to the referral.",
        })
    elif odd_endorsed >= 2:
        flags.append({
            "domain": "Oppositional Defiant",
            "severity": "Watch",
            "message": "Subthreshold ODD symptoms -- monitor behaviour across settings.",
        })

    anx_endorsed = _count_endorsed(responses, cfg.ANXIETY_ITEMS)
    if anx_endorsed >= 2:
        flags.append({
            "domain": "Anxiety / Mood",
            "severity": "High",
            "message": "Anxiety or mood symptoms screen positive. Consider child psychology "
                       "review alongside ADHD assessment.",
        })
    elif anx_endorsed >= 1:
        flags.append({
            "domain": "Anxiety / Mood",
            "severity": "Watch",
            "message": "Single anxiety/mood concern raised -- ask parent + teacher to monitor.",
        })

    return flags


def score(responses: dict) -> ScreeningResult:
    """Compute the full ScreeningResult from a flat dict of item_id -> response."""
    inatt_endorsed = _count_endorsed(responses, cfg.INATTENTION_ITEMS)
    hi_endorsed = _count_endorsed(responses, cfg.HYPERACTIVITY_ITEMS)
    inatt_total = _sum_items(responses, cfg.INATTENTION_ITEMS)
    hi_total = _sum_items(responses, cfg.HYPERACTIVITY_ITEMS)
    presentation = _presentation(inatt_endorsed, hi_endorsed)
    impairment_count, impaired_areas = _impairment(responses)
    risk_level, explanation = _risk_level(inatt_endorsed, hi_endorsed, impairment_count)
    flags = _comorbidity_flags(responses)

    return ScreeningResult(
        inattention_endorsed=inatt_endorsed,
        hyperactivity_endorsed=hi_endorsed,
        inattention_total=inatt_total,
        hyperactivity_total=hi_total,
        presentation=presentation,
        impairment_count=impairment_count,
        impaired_areas=impaired_areas,
        risk_level=risk_level,
        rule_based_risk_code=cfg.RISK_MAP[risk_level],
        flags=flags,
        explanation=explanation,
    )


def cross_informant_agreement(parent: ScreeningResult, teacher: ScreeningResult) -> dict:
    """Compare a parent + teacher pair and surface clinically meaningful disagreement."""
    same = parent.risk_level == teacher.risk_level
    summary = {
        "parent_risk": parent.risk_level,
        "teacher_risk": teacher.risk_level,
        "agreement": "Full" if same else "Disagreement",
        "notes": [],
    }
    if not same:
        codes = sorted([parent.rule_based_risk_code, teacher.rule_based_risk_code])
        if codes == [0, 2]:
            summary["notes"].append(
                "Wide disagreement (Low vs High) -- ADHD often presents differently across "
                "settings. Recommend specialist review regardless."
            )
        else:
            summary["notes"].append(
                "Partial disagreement -- ADHD often presents differently between home and "
                "school; the higher rating should drive the referral decision."
            )
    if abs(parent.inattention_endorsed - teacher.inattention_endorsed) >= 4:
        summary["notes"].append(
            "Large gap in inattention items between parent and teacher -- consider whether "
            "task demand differs between home and school."
        )
    if abs(parent.hyperactivity_endorsed - teacher.hyperactivity_endorsed) >= 4:
        summary["notes"].append(
            "Large gap in hyperactivity/impulsivity between parent and teacher -- ask both "
            "raters to describe the contexts."
        )
    return summary
