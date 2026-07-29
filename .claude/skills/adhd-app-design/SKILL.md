---
name: adhd-app-design
description: >
  Design system and build conventions for the ADHD Screening Streamlit app
  (app/ + src/). Load this BEFORE adding a page, changing colors, editing the
  hero/cards/pills, or building any UI so the new work matches the existing
  "Editorial Navy" look and the app's clinical/privacy conventions. Triggers:
  "restyle", "recolor", "new page", "add a chart", "the banner", "role card",
  "risk result", "make it interactive" for this app.
---

# ADHD Screening App — Design System & Conventions

This app is a **non-diagnostic ADHD screening + referral tool for Nigeria**
(ages 4–15). It is a multi-page Streamlit app (`st.navigation`) with a
role-gated sidebar (Parent / Teacher / Clinician). Keep every change consistent
with the rules below.

## Golden rules (do not violate)

1. **Screening, never diagnosis.** Every result surface must keep the
   "screening only — not a diagnosis" reminder. Never soften it.
2. **Privacy: initials only.** No full names. Children are keyed by an opaque
   Study ID + first/last initial. Never add a field that stores PII.
3. **Colors come from one place.** Do NOT hardcode new hex values inline. Use
   the palette constants (see below). The app historically scattered ~70 inline
   hexes across 9 files — that is the anti-pattern we are moving away from.
4. **HTML blocks use `unsafe_allow_html=True`** and follow the existing
   card/pill patterns — don't invent new visual components when one exists.

## Palette — "Editorial Navy" (current, keep unless told otherwise)

| Role | Hex | Use |
|------|-----|-----|
| Primary (navy-900) | `#1e3a8a` | CTAs, links, active nav, card top-borders |
| Primary deep | `#1e293b` | banner gradient end |
| Accent (amber-700) | `#b45309` | banner underline, "Screening not Diagnosis" badge |
| Teacher accent | `#7c2d12` | teacher role color |
| Clinician accent | `#166534` | clinician role color, "verified" badge |
| Background | `#fafaf9` | warm stone page bg |
| Card / sidebar bg | `#ffffff` | cards |
| Body text | `#1c1917` / `#44403c` / `#57534e` | primary / secondary / muted |
| Border | `#e7e5e4` | card + sidebar borders |
| Risk — Low | `#166534` | forest |
| Risk — Moderate | `#b45309` | amber |
| Risk — High | `#991b1b` | crimson |

**Centralization plan:** these belong in `app/_theme.py` as named constants
(`PRIMARY`, `ACCENT`, `RISK_LOW`, …). When you touch a file that still has
inline hexes, migrate them to the constant. The palette values live in
`_shared.py` (`RISK_COLORS`, `ACCENT_COLOR`) and the `header()` CSS block today.

## Typography

- **Headings:** Georgia / serif (`font-family: Georgia, 'Times New Roman', serif`),
  slightly tightened letter-spacing. Set globally in `header()`.
- **Body:** sans-serif (Streamlit default).
- This serif-heading / sans-body split is the editorial signature — keep it.

## Reusable component patterns (already defined — reuse, don't reinvent)

- `header()` — injects the global CSS (`.pill`, `.info-card`, `.role-card`,
  sidebar border). Call once per page, first.
- `app_banner()` — navy gradient hero with eyebrow + serif H1 + badges.
- `render_screening_hero(rater_type)` — role-colored hero + "what to expect" chips.
- `role_card(slot, body_html, accent)` — home role cards (optional top image).
- `risk_pill(level)` → `.pill .risk-pill-{low|moderate|high}`.
- `info-card` — white card, colored left border. Used for callouts everywhere.
- `_step(number, title, sub)` — numbered stage marker for long forms.

CSS classes live in the `header()` string in `app/_shared.py`. Add new shared
classes there, not inline per page.

## Interactivity patterns to prefer

- **Live form progress:** count answered items and show `st.progress(...)` +
  an "X of N answered" caption. Wrap in `st.fragment` if it should update
  without re-running the whole page.
- **Risk gauge:** render the risk level as a color-coded donut/gauge (Plotly
  `go.Indicator` or an inline SVG using `RISK_COLORS`) instead of a bare
  `st.metric`. Keep the numeric metrics alongside it.
- **Hover/animation:** add `transition:` + `:hover` rules to the shared CSS
  (cards lift slightly, buttons darken). Keep it subtle — this is a clinical tool.
- **Hospital map (heavier):** `hospitals.py` has NO lat/long. A real map needs
  coordinates added per hospital (or state-centroid approximation) first. Treat
  as a data task, not just a UI task.

## Running the app locally

The `.venv` may be missing (it was deleted in a folder move). Rebuild before running:

```powershell
cd "C:\Users\hp\Desktop\GROUP 7\adhd-screening-nigeria"
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\streamlit run app/streamlit_app.py
```

The model artifacts in `models/` must exist or screening pages call `st.stop()`;
retrain with `python -m src.train` if missing.

## File map (source of truth — README is stale)

- `app/streamlit_app.py` — entry, `st.navigation`, role gating.
- `app/_shared.py` — CSS, forms, results, PDF, hero, risk logic. **Most edits land here.**
- `app/_pages/` — home, about, parent, teacher, clinician, feedback, faq, consult.
- `app/_assets.py`, `app/_illustrations.py` — optional images + inline SVGs.
- `src/` — scoring (DSM-5 rules), instruments (forms), hospitals, model, pdf.
