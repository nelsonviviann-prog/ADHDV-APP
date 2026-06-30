# Early Detection of ADHD in the Nigerian Population Using AI

Master's Capstone Research Project — **ADHD Screening & Referral Support Tool** (non-diagnostic) for Nigerian pediatric demographics, ages 4–15.

> **Screening, not diagnosis.** This tool assists overloaded pediatricians by triaging children before specialist consultation. It is built specifically for the Nigerian healthcare context — every state + FCT is covered in the referral directory.

## What's in this app

- **Vanderbilt-style questionnaire** (NICHQ-aligned, public domain) — Parent form (47 items) and Teacher form (35 items).
- **DSM-5 18 core symptoms** (9 inattention + 9 hyperactivity/impulsivity) plus performance impairment (8 items) and brief ODD/anxiety screens.
- **Rule-based DSM-5 scoring** as the authoritative result, with a **Random Forest** ML second opinion for calibration.
- **Cross-informant agreement** — flag where parent and teacher disagree (clinically meaningful signal).
- **Multi-rater roles** — Parent, Teacher, and Clinician workflows on separate pages.
- **Auto-routed Nigerian referrals** — every state + FCT mapped to nearest tertiary mental-health facility (Federal Neuro-Psychiatric Hospitals, Federal Teaching Hospitals, State Teaching Hospitals).
- **Clinician PDF export** — downloadable report the parent can carry to the appointment.
- **Local SQLite persistence** — child profiles + longitudinal screening sessions, no cloud, offline-friendly.
- **i18n scaffolding** — English ships today; YO / IG / HA translation slots ready.

## Project layout

```
adhd-screening-nigeria/
├── README.md
├── requirements.txt
├── .streamlit/config.toml         # theme (teal primary, accessible)
├── data/                          # synthetic CSV + SQLite DB
├── models/                        # adhd_screening_rf_model.joblib + plots
├── src/
│   ├── config.py                  # constants, feature lists, thresholds
│   ├── instruments.py             # Vanderbilt-style Parent + Teacher forms
│   ├── hospitals.py               # All 36 states + FCT directory + routing
│   ├── scoring.py                 # DSM-5 rule-based scorer + agreement
│   ├── database.py                # SQLite (children, sessions, raters)
│   ├── i18n.py                    # Translation scaffolding
│   ├── pdf_report.py              # ReportLab clinician PDF
│   ├── train.py                   # Synthetic data + 3 models
│   └── predict.py                 # JSON-in / report-out CLI
├── app/
│   ├── streamlit_app.py           # Landing page + role chooser
│   ├── _shared.py                 # Reusable form, results, PDF helpers
│   └── pages/
│       ├── 1_Parent_Screening.py
│       ├── 2_Teacher_Screening.py
│       ├── 3_Clinician_Dashboard.py
│       └── 4_About.py
└── notebook/
    └── ADHD_Screening_Capstone.ipynb   # The original capstone notebook
```

## Setup

```powershell
# 1. (one time) create venv
C:\Users\hp\AppData\Local\Programs\Python\Python311\python.exe -m venv .venv

# 2. activate
.\.venv\Scripts\Activate.ps1

# 3. install deps
pip install -r requirements.txt
```

## Train

```powershell
python -m src.train
```

Produces `models/adhd_screening_rf_model.joblib`, metadata, and four PNG plots (EDA, comparison, confusion, feature importance).

## CLI prediction

```powershell
# Built-in demo (no JSON file needed)
python -m src.predict --demo Primary High

# Or feed a real payload
python -m src.predict --file path/to/responses.json
```

## Run the web app

```powershell
streamlit run app/streamlit_app.py
```

Open the printed URL (typically <http://localhost:8501>) and pick a role:

- **Parent Screening** — fill the home-context form; receive a Study ID.
- **Teacher Screening** — enter the Study ID, fill the classroom-context form; the system pairs the two ratings.
- **Clinician Dashboard** — search by Study ID, view cross-informant agreement, download PDF.

## Open the original capstone notebook

```powershell
jupyter notebook notebook/ADHD_Screening_Capstone.ipynb
```

The notebook is preserved as the original Steps 1–9 capstone artifact (kept for the academic defense). The `src/` + `app/` rebuild is the production-style application around it.

## Risk thresholds (DSM-5 aligned)

| Risk | Symptoms endorsed (Often or Very Often) | Impairment | Action |
|------|----------------------------------------|------------|--------|
| **Low** | < 3 in both subscales | — | Standard pediatric guidance |
| **Moderate** | 3–5 in either subscale, OR ≥6 without impairment | < 2 impaired areas | Watchful monitoring, follow-up in 3–6 months |
| **High** | ≥ 6 in either subscale | ≥ 2 impaired areas | Immediate referral to the routed Nigerian teaching hospital |

## Hospital coverage

All 36 Nigerian states + FCT mapped to nearest tertiary mental-health facility. Routing priority within a state:

1. Federal Neuro-Psychiatric Hospital (best clinical fit for ADHD).
2. Federal Teaching Hospital.
3. State Teaching Hospital.
4. Falls back to nearest hospital in the same geopolitical zone if none in-state.

## Clinician access — onboarding & revocation

Clinicians access the dashboard via a **personal access code** (e.g. `dr-adekoya-7a3b9c`). Each code maps to a named clinician; every action they take in the dashboard is logged with their name in an audit table.

### Generate a new clinician code

```powershell
python -m scripts.new_clinician_code "Dr. Adekoya"
```

The script prints a TOML line ready to paste.

### Register the code (production)

1. Streamlit Cloud → your app → ⋮ menu → **Settings → Secrets**.
2. Add (or extend) the `[clinician_accounts]` block:

   ```toml
   [clinician_accounts]
   "dr-adekoya-7a3b9c"    = "Dr. Adekoya"
   "nurse-okonkwo-4f8e2d" = "Nurse Okonkwo"
   ```

3. Click **Save**. Secrets reload live; no redeploy needed.

### Send the code

WhatsApp / SMS / email the code to the clinician. They enter it at the **Clinician access code** field on the Home page.

### Revoke a clinician

Delete their line from the `[clinician_accounts]` block and click **Save**. The code is invalid immediately.

### Development fallback

If no `clinician_accounts` block is set, the app falls back to a single dev code `adhd-2026` mapped to "Dev Clinician" and shows a visible warning on the passcode page. Replace before sharing publicly.

## Privacy

- No PII leaves the deployment. Only first/last initial + Study ID are stored per child.
- Clinician audit log records: clinician name, action (`sign_in` / `view_dashboard` / `view_study`), target Study ID (when applicable), and UTC timestamp.
- SQLite database lives at `data/screening_sessions.db` (local) or in the Streamlit Cloud container (ephemeral; resets on every redeploy).
- The trained model runs locally; no cloud, no telemetry, no analytics.
