"""
Generate a clinician-ready PDF report of one (or two) screening sessions
for the parent to carry to their nearest Nigerian teaching hospital.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .hospitals import Hospital, referral_recommendations
from .scoring import ScreeningResult, cross_informant_agreement


# Editorial Navy palette -- matches Streamlit theme.
PRIMARY = colors.HexColor("#1e3a8a")  # navy-900   -- headings, table headers
ACCENT = colors.HexColor("#7c2d12")   # burgundy   -- secondary emphasis
HIGH = colors.HexColor("#991b1b")     # crimson-900
MOD = colors.HexColor("#b45309")      # amber-700
LOW = colors.HexColor("#166534")      # forest-800
MUTED = colors.HexColor("#57534e")    # stone-600  -- body / metadata


def _risk_color(risk_level: str):
    return {"High Risk": HIGH, "Moderate Risk": MOD, "Low Risk": LOW}.get(risk_level, MUTED)


def build_pdf(
    *,
    child: dict,
    parent_result: ScreeningResult | None,
    teacher_result: ScreeningResult | None,
    referrals: list[Hospital] | None = None,
) -> bytes:
    """Return raw PDF bytes for download."""
    if referrals is None and child.get("state"):
        referrals = referral_recommendations(child["state"])

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="ADHD Screening Report",
        author="ADHD Screening & Referral Support Tool",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=PRIMARY, fontSize=18, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=ACCENT, fontSize=13, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10, leading=14)
    muted = ParagraphStyle("muted", parent=body, textColor=MUTED, fontSize=9, leading=12)

    story = []
    story.append(Paragraph("ADHD Screening Report (Non-Diagnostic)", h1))
    story.append(Paragraph(
        f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | "
        f"Study ID: <b>{child.get('study_id', '-')}</b>",
        muted,
    ))
    story.append(Spacer(1, 6))

    # Child summary
    child_rows = [
        ["Age", str(child.get("age", "-"))],
        ["Gender", child.get("gender", "-")],
        ["School level", child.get("school_level", "-")],
        ["State of residence", child.get("state", "-")],
        ["Initials", f"{child.get('first_name_initial','')}. {child.get('last_name_initial','')}."],
    ]
    tbl = Table(child_rows, colWidths=[55 * mm, 100 * mm])
    tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    # Rater results
    for label, res in (("Parent / Caregiver", parent_result), ("Teacher", teacher_result)):
        if res is None:
            continue
        story.append(Paragraph(f"{label} screening result", h2))
        risk_para = Paragraph(
            f"<font color='{_risk_color(res.risk_level).hexval()}'><b>{res.risk_level}</b></font> | "
            f"Presentation: <b>{res.presentation}</b>",
            body,
        )
        story.append(risk_para)
        story.append(Spacer(1, 4))

        rater_tbl = Table([
            ["Inattention symptoms endorsed (>= Often)", f"{res.inattention_endorsed} / 9"],
            ["Hyperactivity / Impulsivity endorsed",     f"{res.hyperactivity_endorsed} / 9"],
            ["Performance areas impaired",                f"{res.impairment_count} / 8"],
            ["Inattention raw score",                     f"{res.inattention_total} / 36"],
            ["Hyperactivity raw score",                   f"{res.hyperactivity_total} / 36"],
        ], colWidths=[80 * mm, 75 * mm])
        rater_tbl.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(rater_tbl)
        story.append(Spacer(1, 4))

        for explain in res.explanation:
            story.append(Paragraph(f"- {explain}", muted))

        if res.flags:
            story.append(Spacer(1, 4))
            story.append(Paragraph("Co-occurring concerns flagged:", body))
            for f in res.flags:
                color = HIGH if f["severity"] == "High" else MOD
                story.append(Paragraph(
                    f"<font color='{color.hexval()}'><b>[{f['severity']}]</b></font> "
                    f"{f['domain']}: {f['message']}",
                    body,
                ))
        story.append(Spacer(1, 10))

    # Cross-informant agreement
    if parent_result and teacher_result:
        story.append(Paragraph("Cross-informant agreement", h2))
        agreement = cross_informant_agreement(parent_result, teacher_result)
        story.append(Paragraph(
            f"<b>{agreement['agreement']}</b> | Parent: {agreement['parent_risk']} | "
            f"Teacher: {agreement['teacher_risk']}",
            body,
        ))
        for note in agreement["notes"]:
            story.append(Paragraph(f"- {note}", muted))
        story.append(Spacer(1, 10))

    # Referrals
    if referrals:
        story.append(Paragraph("Recommended tertiary referrals", h2))
        rows = [["Hospital", "City / State", "Type"]]
        for h in referrals:
            kind = {
                "federal_neuro_psychiatric": "Federal Neuro-Psychiatric",
                "federal_teaching": "Federal Teaching Hospital",
                "state_teaching": "State Teaching Hospital",
                "specialist": "Specialist Hospital",
            }.get(h.kind, h.kind)
            rows.append([f"{h.name} ({h.abbreviation})", f"{h.city}, {h.state}", kind])
        tbl2 = Table(rows, colWidths=[75 * mm, 55 * mm, 45 * mm])
        tbl2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(tbl2)
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Important:</b> This document is a screening aid, NOT a clinical "
        "diagnosis. Diagnosis of ADHD requires direct evaluation by a qualified "
        "child psychiatrist or pediatrician. Bring this report with you to the "
        "referral appointment.",
        muted,
    ))

    doc.build(story)
    return buf.getvalue()
