"""Project-wide constants. One source of truth for feature names, mappings,
file paths, and DSM-5 thresholds.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "screening_sessions.db"

MODEL_PATH = MODELS_DIR / "adhd_screening_rf_model.joblib"
META_PATH = MODELS_DIR / "adhd_model_metadata.joblib"
DATASET_CSV = DATA_DIR / "adhd_synthetic_dataset.csv"

GENDER_MAP = {"Male": 1, "Female": 0}
SCHOOL_MAP = {"Nursery": 0, "Primary": 1, "Junior Secondary": 2, "Senior Secondary": 3}
RATER_MAP = {"Parent": 0, "Teacher": 1}
RISK_MAP = {"Low Risk": 0, "Moderate Risk": 1, "High Risk": 2}
RISK_REVERSE = {v: k for k, v in RISK_MAP.items()}

LIKERT_OPTIONS = {
    "Never (0)": 0,
    "Rarely (1)": 1,
    "Sometimes (2)": 2,
    "Often (3)": 3,
    "Very Often (4)": 4,
}
LIKERT_LABELS = {v: k.split(" (")[0] for k, v in LIKERT_OPTIONS.items()}

PERFORMANCE_OPTIONS = {
    "Excellent (1)": 1,
    "Above Average (2)": 2,
    "Average (3)": 3,
    "Somewhat of a Problem (4)": 4,
    "Problematic (5)": 5,
}

# Aligned with DSM-5: a symptom is "endorsed" when the response is Often (3) or
# Very Often (4) on the 0-4 Likert. Vanderbilt uses 0-3 and endorses at >=2;
# we use 0-4 (per the capstone schema) and endorse at >=3.
ENDORSEMENT_THRESHOLD = 3

# DSM-5: 6 or more endorsed symptoms in either subscale meets the symptom
# count threshold for diagnosis (in children).
DSM5_SYMPTOM_THRESHOLD = 6

INATTENTION_ITEMS = [
    "inatt_1_careless_mistakes",
    "inatt_2_sustaining_attention",
    "inatt_3_not_listening",
    "inatt_4_not_following_through",
    "inatt_5_organizing_tasks",
    "inatt_6_avoids_mental_effort",
    "inatt_7_loses_things",
    "inatt_8_easily_distracted",
    "inatt_9_forgetful",
]
HYPERACTIVITY_ITEMS = [
    "hyper_1_fidgets",
    "hyper_2_leaves_seat",
    "hyper_3_runs_climbs",
    "hyper_4_cannot_play_quietly",
    "hyper_5_on_the_go",
    "hyper_6_talks_excessively",
    "hyper_7_blurts_answers",
    "hyper_8_difficulty_waiting",
    "hyper_9_interrupts",
]
CORE_SYMPTOM_ITEMS = INATTENTION_ITEMS + HYPERACTIVITY_ITEMS

PERFORMANCE_ITEMS = [
    "perf_overall_school",
    "perf_reading",
    "perf_writing",
    "perf_mathematics",
    "perf_relations_parents_or_classroom",
    "perf_relations_siblings_or_groupwork",
    "perf_relations_peers",
    "perf_organized_activities",
]
ODD_ITEMS = [
    "odd_1_loses_temper",
    "odd_2_argues_adults",
    "odd_3_defies_rules",
    "odd_4_deliberately_annoys",
]
ANXIETY_ITEMS = [
    "anx_1_fearful_anxious_worried",
    "anx_2_low_self_esteem",
    "anx_3_sad_unhappy_depressed",
]

# Demographics + rater + 18 core + 8 performance + 4 ODD + 3 anxiety = 36 features
ML_FEATURE_COLS = (
    ["Age", "Gender", "School_Level", "Rater_Type"]
    + CORE_SYMPTOM_ITEMS
    + PERFORMANCE_ITEMS
    + ODD_ITEMS
    + ANXIETY_ITEMS
)

REFERRAL_THRESHOLDS = {
    "high_min_symptom_count": DSM5_SYMPTOM_THRESHOLD,
    "high_min_impairment_count": 2,
    "moderate_min_symptom_count": 3,
}
