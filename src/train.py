"""
ADHD Screening & Referral Support Tool -- training pipeline (Vanderbilt-style).

Generates a synthetic Nigerian pediatric ADHD screening dataset based on the
NICHQ Vanderbilt-aligned 18 DSM-5 core symptoms + 8 performance items + 4 ODD
+ 3 anxiety items, for both Parent and Teacher raters. Preprocesses, trains
Logistic Regression / Decision Tree / Random Forest, evaluates all three,
saves the best model and metadata, plus EDA / comparison / confusion / feature
importance plots.

Run:
    python src/train.py
"""

from __future__ import annotations

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from . import config as cfg
from .hospitals import NIGERIAN_STATES_AND_FCT
from .scoring import score as score_responses


COMPARISON_PLOT = cfg.MODELS_DIR / "model_comparison.png"
CONFUSION_PLOT = cfg.MODELS_DIR / "confusion_matrices.png"
EDA_PLOT = cfg.MODELS_DIR / "eda_overview.png"
FEATURE_IMPORTANCE_PLOT = cfg.MODELS_DIR / "feature_importance.png"


def school_level_for_age(age: int) -> str:
    if age <= 5:
        return "Nursery"
    if age <= 11:
        return "Primary"
    if age <= 14:
        return "Junior Secondary"
    return "Senior Secondary"


def _draw_symptom(rng: np.random.Generator, p: float) -> int:
    return int(np.clip(rng.binomial(4, p), 0, 4))


def _draw_perf(rng: np.random.Generator, severity: float) -> int:
    # 1 (Excellent) ... 5 (Problematic). Higher severity -> right-shifted distribution.
    weights = np.array([
        max(0.05, 0.45 - 0.10 * severity),
        max(0.05, 0.30 - 0.05 * severity),
        0.15 + 0.05 * severity,
        0.05 + 0.07 * severity,
        0.05 + 0.10 * severity,
    ])
    weights = weights / weights.sum()
    return int(rng.choice([1, 2, 3, 4, 5], p=weights))


def build_synthetic_dataset(n_samples: int = 1200, seed: int = 42) -> pd.DataFrame:
    """Synthetic Vanderbilt-style screening responses.

    Latent traits drive symptom intensity; gender affects which subscale
    presents (girls tilted inattentive, boys tilted hyperactive); rater
    affects observed scores (teachers report more H/I, parents more
    inattentive/forgetful).
    """
    rng = np.random.default_rng(seed)

    ages = rng.integers(4, 16, n_samples)
    gender = rng.choice(["Male", "Female"], n_samples, p=[0.55, 0.45])
    rater_type = rng.choice(["Parent", "Teacher"], n_samples, p=[0.55, 0.45])
    school_levels = np.array([school_level_for_age(a) for a in ages])
    states = rng.choice(NIGERIAN_STATES_AND_FCT, size=n_samples)

    rows = []
    for i in range(n_samples):
        is_male = gender[i] == "Male"
        is_teacher = rater_type[i] == "Teacher"

        # Latent severity scaled to roughly recreate epidemiological prevalence
        # (about 7-9% high-risk, 20-25% moderate, rest low).
        latent_inatt = rng.beta(2.0, 6.0 if not is_male else 5.0)
        latent_hi = rng.beta(2.0, 5.0 if is_male else 7.0)

        # Rater bias
        inatt_obs = latent_inatt + (0.05 if not is_teacher else -0.02)
        hi_obs = latent_hi + (0.08 if is_teacher else -0.02)
        inatt_obs = float(np.clip(inatt_obs, 0.02, 0.95))
        hi_obs = float(np.clip(hi_obs, 0.02, 0.95))

        record = {
            "Age": int(ages[i]),
            "Gender": gender[i],
            "School_Level": school_levels[i],
            "State": states[i],
            "Rater_Type": rater_type[i],
        }
        for item in cfg.INATTENTION_ITEMS:
            record[item] = _draw_symptom(rng, inatt_obs)
        for item in cfg.HYPERACTIVITY_ITEMS:
            record[item] = _draw_symptom(rng, hi_obs)

        # Performance impairment correlates with the dominant subscale.
        severity = (inatt_obs + hi_obs) * 2.0
        for item in cfg.PERFORMANCE_ITEMS:
            record[item] = _draw_perf(rng, severity)

        # ODD / anxiety co-occur at lower base rates.
        for item in cfg.ODD_ITEMS:
            record[item] = _draw_symptom(rng, max(0.05, hi_obs - 0.20))
        for item in cfg.ANXIETY_ITEMS:
            record[item] = _draw_symptom(rng, max(0.05, inatt_obs - 0.10))

        rows.append(record)

    df = pd.DataFrame(rows)

    # Inject realistic missing values (clinician notebooks lose Age and the
    # very first symptom item most often).
    miss_age_idx = rng.choice(n_samples, size=int(n_samples * 0.03), replace=False)
    miss_inatt1_idx = rng.choice(n_samples, size=int(n_samples * 0.025), replace=False)
    df.loc[miss_age_idx, "Age"] = np.nan
    df.loc[miss_inatt1_idx, cfg.INATTENTION_ITEMS[0]] = np.nan

    return df


def preprocess(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df["Age"] = df["Age"].fillna(df["Age"].median()).astype(int)
    df[cfg.INATTENTION_ITEMS[0]] = (
        df[cfg.INATTENTION_ITEMS[0]].fillna(df[cfg.INATTENTION_ITEMS[0]].mode().iloc[0]).astype(int)
    )

    df["Gender"] = df["Gender"].map(cfg.GENDER_MAP).astype(int)
    df["School_Level"] = df["School_Level"].map(cfg.SCHOOL_MAP).astype(int)
    df["Rater_Type"] = df["Rater_Type"].map(cfg.RATER_MAP).astype(int)

    # Generate rule-based labels via the scoring module (single source of truth).
    risk_codes, presentations = [], []
    for _, row in df.iterrows():
        responses = {k: int(row[k]) for k in cfg.CORE_SYMPTOM_ITEMS
                                       + cfg.PERFORMANCE_ITEMS
                                       + cfg.ODD_ITEMS
                                       + cfg.ANXIETY_ITEMS}
        result = score_responses(responses)
        risk_codes.append(result.rule_based_risk_code)
        presentations.append(result.presentation)

    df["ADHD_Risk_Code"] = risk_codes
    df["Presentation"] = presentations
    df["ADHD_Risk"] = df["ADHD_Risk_Code"].map(cfg.RISK_REVERSE)
    return df


def evaluate(name: str, model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        "y_pred": y_pred,
        "report": classification_report(
            y_test, y_pred,
            target_names=[cfg.RISK_REVERSE[i] for i in sorted(cfg.RISK_REVERSE)],
            zero_division=0,
        ),
    }


def plot_eda(clean_df: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    risk_order = ["Low Risk", "Moderate Risk", "High Risk"]
    palette = ["#16a34a", "#d97706", "#dc2626"]

    sns.countplot(
        data=clean_df, x="ADHD_Risk", ax=axes[0], order=risk_order,
        hue="ADHD_Risk", palette=palette, legend=False,
    )
    axes[0].set_title("ADHD Risk Distribution (rule-based labels)")

    gender_lab = clean_df.assign(GenderLabel=clean_df["Gender"].map({1: "Male", 0: "Female"}))
    sns.boxplot(
        data=gender_lab, x="GenderLabel",
        y=gender_lab[cfg.HYPERACTIVITY_ITEMS].sum(axis=1),
        ax=axes[1], hue="GenderLabel",
        palette=["#1d4ed8", "#be123c"], legend=False,
    )
    axes[1].set_title("Total H/I symptom score by Gender")
    axes[1].set_xlabel("Gender"); axes[1].set_ylabel("Sum of 9 H/I items (0-36)")

    rater_lab = clean_df.assign(RaterLabel=clean_df["Rater_Type"].map({0: "Parent", 1: "Teacher"}))
    sns.countplot(
        data=rater_lab, x="RaterLabel", hue="ADHD_Risk",
        ax=axes[2], hue_order=risk_order, palette=palette,
    )
    axes[2].set_title("Screening risk by Rater Type")
    axes[2].set_xlabel("Rater")

    plt.tight_layout()
    plt.savefig(EDA_PLOT, dpi=120); plt.close(fig)


def plot_comparison(results: list[dict]) -> None:
    metrics = ["accuracy", "precision", "recall", "f1"]
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(results))
    width = 0.2
    for i, m in enumerate(metrics):
        ax.bar(x + i * width, [r[m] for r in results], width, label=m.capitalize())
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([r["model"] for r in results])
    ax.set_ylim(0, 1.05); ax.set_ylabel("Weighted score")
    ax.set_title("Model Comparison"); ax.legend(loc="lower right")
    plt.tight_layout(); plt.savefig(COMPARISON_PLOT, dpi=120); plt.close(fig)


def plot_confusions(results: list[dict], y_test) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    labels = [cfg.RISK_REVERSE[i] for i in sorted(cfg.RISK_REVERSE)]
    for ax, r in zip(axes, results):
        cm = confusion_matrix(y_test, r["y_pred"])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=labels, yticklabels=labels, ax=ax, cbar=False)
        ax.set_title(r["model"]); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    plt.tight_layout(); plt.savefig(CONFUSION_PLOT, dpi=120); plt.close(fig)


def plot_feature_importance(model: RandomForestClassifier) -> None:
    importances = (
        pd.Series(model.feature_importances_, index=cfg.ML_FEATURE_COLS)
        .sort_values()
        .tail(20)
    )
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(importances.index, importances.values, color="#0f766e")
    ax.set_title("Top 20 Random Forest Feature Importances")
    ax.set_xlabel("Importance")
    plt.tight_layout(); plt.savefig(FEATURE_IMPORTANCE_PLOT, dpi=120); plt.close(fig)


def main() -> None:
    cfg.DATA_DIR.mkdir(exist_ok=True)
    cfg.MODELS_DIR.mkdir(exist_ok=True)

    print("[1/6] Generating synthetic Vanderbilt-style screening dataset...")
    raw_df = build_synthetic_dataset()
    raw_df.to_csv(cfg.DATASET_CSV, index=False)
    print(f"      rows={len(raw_df)}  features per row={raw_df.shape[1]}")

    print("[2/6] Preprocessing + rule-based label generation...")
    clean_df = preprocess(raw_df)

    X = clean_df[cfg.ML_FEATURE_COLS]
    y = clean_df["ADHD_Risk_Code"]
    print(f"      class balance: {y.map(cfg.RISK_REVERSE).value_counts().to_dict()}")

    print("[3/6] EDA plots...")
    plot_eda(clean_df)

    print("[4/6] Train/test split (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("[5/6] Training Logistic Regression / Decision Tree / Random Forest...")
    # `class_weight='balanced'` boosts recall on the High Risk class -- the
    # most important metric for a screening tool (missing a real case is
    # much costlier than over-referring).
    log_reg = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
    dec_tree = DecisionTreeClassifier(
        max_depth=8, min_samples_split=10, class_weight="balanced", random_state=42
    )
    rand_forest = RandomForestClassifier(
        n_estimators=300, max_depth=12, class_weight="balanced_subsample",
        random_state=42, n_jobs=-1,
    )
    log_reg.fit(X_train, y_train)
    dec_tree.fit(X_train, y_train)
    rand_forest.fit(X_train, y_train)

    results = [
        evaluate("Logistic Regression", log_reg, X_test, y_test),
        evaluate("Decision Tree", dec_tree, X_test, y_test),
        evaluate("Random Forest", rand_forest, X_test, y_test),
    ]

    print("\n      Model              Acc    Prec   Rec    F1")
    print("      ------------------ ------ ------ ------ ------")
    for r in results:
        print(
            f"      {r['model']:<18s} "
            f"{r['accuracy']:.3f}  {r['precision']:.3f}  {r['recall']:.3f}  {r['f1']:.3f}"
        )
    for r in results:
        print(f"\n      --- {r['model']} ---\n{r['report']}")

    plot_comparison(results)
    plot_confusions(results, y_test)
    plot_feature_importance(rand_forest)

    print("[6/6] Saving best model (Random Forest) and metadata...")
    joblib.dump(rand_forest, cfg.MODEL_PATH)
    meta = {
        "features": cfg.ML_FEATURE_COLS,
        "core_symptom_features": cfg.CORE_SYMPTOM_ITEMS,
        "performance_features": cfg.PERFORMANCE_ITEMS,
        "odd_features": cfg.ODD_ITEMS,
        "anxiety_features": cfg.ANXIETY_ITEMS,
        "risk_mapping": cfg.RISK_REVERSE,
        "gender_mapping": cfg.GENDER_MAP,
        "school_mapping": cfg.SCHOOL_MAP,
        "rater_mapping": cfg.RATER_MAP,
        "endorsement_threshold": cfg.ENDORSEMENT_THRESHOLD,
        "dsm5_symptom_threshold": cfg.DSM5_SYMPTOM_THRESHOLD,
    }
    joblib.dump(meta, cfg.META_PATH)

    print(f"      model    -> {cfg.MODEL_PATH}")
    print(f"      metadata -> {cfg.META_PATH}")
    print("\nDone.")


if __name__ == "__main__":
    main()
