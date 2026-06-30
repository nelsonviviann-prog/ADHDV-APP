"""
ADHD Screening & Referral Support Tool -- CLI prediction (Vanderbilt-style).

Reads a single child screening from JSON on stdin (or a path), runs the
Random Forest model + rule-based scoring, and prints the report (or JSON if
--json is passed).

Example:
    python -m src.predict --demo Primary High
    python -m src.predict --json --file path/to/responses.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

from . import config as cfg
from .hospitals import referral_recommendations
from .scoring import score as rule_based_score


def _load_artifacts():
    if not cfg.MODEL_PATH.exists() or not cfg.META_PATH.exists():
        raise FileNotFoundError(
            "Model artifacts not found. Run `python -m src.train` first.\n"
            f"  expected: {cfg.MODEL_PATH}\n  expected: {cfg.META_PATH}"
        )
    return joblib.load(cfg.MODEL_PATH), joblib.load(cfg.META_PATH)


def _build_feature_row(payload: dict, meta: dict) -> pd.DataFrame:
    row = {
        "Age": int(payload["age"]),
        "Gender": meta["gender_mapping"].get(payload["gender"], 0),
        "School_Level": meta["school_mapping"].get(payload["school_level"], 1),
        "Rater_Type": meta["rater_mapping"].get(payload.get("rater_type", "Parent"), 0),
    }
    responses = payload["responses"]
    for k in cfg.CORE_SYMPTOM_ITEMS + cfg.PERFORMANCE_ITEMS + cfg.ODD_ITEMS + cfg.ANXIETY_ITEMS:
        row[k] = int(responses.get(k, 0))
    return pd.DataFrame([row])[meta["features"]]


def predict_full(payload: dict) -> dict:
    """Run both ML + rule-based scoring on a single payload."""
    model, meta = _load_artifacts()
    feature_row = _build_feature_row(payload, meta)
    ml_class = int(model.predict(feature_row)[0])
    probabilities = model.predict_proba(feature_row)[0]
    ml_risk = meta["risk_mapping"].get(ml_class, "Unknown")

    rule = rule_based_score(payload["responses"])
    referrals = referral_recommendations(payload.get("state", "Lagos"))

    return {
        "ml": {
            "risk_level": ml_risk,
            "class_id": ml_class,
            "probabilities": {
                meta["risk_mapping"][i]: float(p) for i, p in enumerate(probabilities)
            },
        },
        "rule": {
            "risk_level": rule.risk_level,
            "presentation": rule.presentation,
            "inattention_endorsed": rule.inattention_endorsed,
            "hyperactivity_endorsed": rule.hyperactivity_endorsed,
            "impairment_count": rule.impairment_count,
            "explanation": rule.explanation,
            "flags": rule.flags,
        },
        "referrals": [
            {"name": h.name, "abbreviation": h.abbreviation, "city": h.city,
             "state": h.state, "kind": h.kind}
            for h in referrals
        ],
    }


def _demo_payload(school_level: str, severity: str) -> dict:
    """Build a quick demo payload so the CLI runs without a JSON file."""
    map_sev = {"Low": 0, "Moderate": 2, "High": 4}
    s = map_sev.get(severity, 2)
    responses = {k: s for k in cfg.CORE_SYMPTOM_ITEMS}
    responses.update({k: (5 if severity == "High" else 3 if severity == "Moderate" else 2)
                      for k in cfg.PERFORMANCE_ITEMS})
    responses.update({k: max(0, s - 1) for k in cfg.ODD_ITEMS + cfg.ANXIETY_ITEMS})
    return {
        "age": 8, "gender": "Male", "school_level": school_level,
        "rater_type": "Parent", "state": "Lagos",
        "responses": responses,
    }


def _print_report(payload: dict, result: dict) -> None:
    print("=" * 72)
    print(" ADHD Screening Report (Non-Diagnostic)")
    print("=" * 72)
    print(f" Age: {payload['age']}  Gender: {payload['gender']}  "
          f"School: {payload['school_level']}  Rater: {payload.get('rater_type','Parent')}")
    print(f" State: {payload.get('state','-')}")
    print()
    ml = result["ml"]
    rule = result["rule"]
    print(" ML model      :", ml["risk_level"],
          "(probs:", ", ".join(f"{k}={v:.2f}" for k, v in ml["probabilities"].items()), ")")
    print(" Rule-based    :", rule["risk_level"], "|", rule["presentation"])
    print(f"    Inattention endorsed : {rule['inattention_endorsed']} / 9")
    print(f"    H/I endorsed         : {rule['hyperactivity_endorsed']} / 9")
    print(f"    Impaired performance : {rule['impairment_count']} / 8")
    for e in rule["explanation"]:
        print(f"    - {e}")
    if rule["flags"]:
        print(" Comorbidity flags:")
        for f in rule["flags"]:
            print(f"   [{f['severity']}] {f['domain']}: {f['message']}")
    print()
    print(" Recommended Nigerian referrals (top 5):")
    for h in result["referrals"]:
        print(f"   - {h['abbreviation']:8s}  {h['name']}  ({h['city']}, {h['state']})")
    print()
    print(" NOTE: Screening only -- NOT a diagnosis.")
    print("=" * 72)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ADHD screening prediction CLI.")
    p.add_argument("--file", type=Path, help="JSON payload path (omit to read stdin).")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a report.")
    p.add_argument("--demo", nargs=2, metavar=("SCHOOL", "SEVERITY"),
                   help="Run a built-in demo, e.g. --demo Primary High")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        payload = _demo_payload(args.demo[0], args.demo[1])
    elif args.file:
        payload = json.loads(args.file.read_text())
    else:
        payload = json.loads(sys.stdin.read())

    result = predict_full(payload)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_report(payload, result)


if __name__ == "__main__":
    main()
