"""End-to-end smoke test: import every module, run a full screening, persist
it to SQLite, generate a PDF. Exits non-zero on any failure.

This is what `streamlit run` would do at the end of one form submission, minus
the streamlit UI. Used to catch regressions without a browser.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402

from src import config as cfg  # noqa: E402
from src import database as db  # noqa: E402
from src.hospitals import referral_recommendations  # noqa: E402
from src.instruments import parent_form, teacher_form  # noqa: E402
from src.pdf_report import build_pdf  # noqa: E402
from src.scoring import cross_informant_agreement, score  # noqa: E402


def make_responses(severity: int) -> dict:
    """severity 0..4 across all symptom items, performance scaled."""
    perf = max(1, min(5, severity + 1))
    out = {k: severity for k in cfg.CORE_SYMPTOM_ITEMS}
    out.update({k: perf for k in cfg.PERFORMANCE_ITEMS})
    out.update({k: max(0, severity - 1) for k in cfg.ODD_ITEMS + cfg.ANXIETY_ITEMS})
    return out


def main() -> int:
    print(":: instruments — parent form size =", len(parent_form()),
          "| teacher form size =", len(teacher_form()))
    assert len(parent_form()) == 33, "parent form should have 18+8+4+3 = 33 items"
    assert len(teacher_form()) == 33, "teacher form should have 33 items"

    print(":: hospitals — Lagos referrals:")
    for h in referral_recommendations("Lagos"):
        print("   ", h.abbreviation, "-", h.name)
    refs = referral_recommendations("Yobe")
    print(":: hospitals — Yobe referrals:")
    for h in refs:
        print("   ", h.abbreviation, "-", h.name, f"({h.state})")

    print(":: model load")
    model = joblib.load(cfg.MODEL_PATH)
    meta = joblib.load(cfg.META_PATH)

    print(":: scoring — High-severity payload (all 4s, all 5s impairment)")
    parent_responses = make_responses(4)
    parent_result = score(parent_responses)
    print("   parent risk =", parent_result.risk_level,
          "| inatt =", parent_result.inattention_endorsed,
          "| h/i =", parent_result.hyperactivity_endorsed,
          "| impaired =", parent_result.impairment_count,
          "| flags =", len(parent_result.flags))
    assert parent_result.risk_level == "High Risk"

    print(":: ML prediction")
    row = {"Age": 8, "Gender": 1, "School_Level": 1, "Rater_Type": 0}
    for k in cfg.CORE_SYMPTOM_ITEMS + cfg.PERFORMANCE_ITEMS + cfg.ODD_ITEMS + cfg.ANXIETY_ITEMS:
        row[k] = parent_responses[k]
    X = pd.DataFrame([row])[meta["features"]]
    pred = int(model.predict(X)[0])
    print("   ML predicted class =", pred, "->", meta["risk_mapping"][pred])

    print(":: scoring — Low-severity teacher payload (all 0s, all 1s impairment)")
    teacher_responses = make_responses(0)
    teacher_result = score(teacher_responses)
    print("   teacher risk =", teacher_result.risk_level)
    assert teacher_result.risk_level == "Low Risk"

    print(":: cross-informant agreement")
    agreement = cross_informant_agreement(parent_result, teacher_result)
    print("   agreement =", agreement["agreement"],
          "| parent =", agreement["parent_risk"],
          "| teacher =", agreement["teacher_risk"])
    print("   notes:")
    for n in agreement["notes"]:
        print("     -", n)

    print(":: database — create child + 2 sessions")
    child = db.upsert_child(
        study_id=None,
        first_name_initial="A", last_name_initial="B",
        age=8, gender="Male", school_level="Primary", state="Lagos",
    )
    print("   study_id =", child["study_id"])
    parent_session_id = db.save_session(
        child_id=child["id"], rater_type="Parent", rater_contact=None,
        responses=parent_responses, result=parent_result,
        ml_prediction=meta["risk_mapping"][pred],
    )
    teacher_session_id = db.save_session(
        child_id=child["id"], rater_type="Teacher", rater_contact="Demo School",
        responses=teacher_responses, result=teacher_result,
        ml_prediction="Low Risk",
    )
    print("   sessions saved:", parent_session_id, teacher_session_id)
    sessions = db.sessions_for_child(child["id"])
    print("   sessions returned for child:", len(sessions))
    assert len(sessions) >= 2

    print(":: PDF — building report")
    pdf = build_pdf(
        child=child,
        parent_result=parent_result,
        teacher_result=teacher_result,
        referrals=referral_recommendations("Lagos"),
    )
    out_pdf = PROJECT_ROOT / "data" / "smoke_test_report.pdf"
    out_pdf.write_bytes(pdf)
    print("   PDF bytes =", len(pdf), "| saved ->", out_pdf)
    assert len(pdf) > 1000

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
