"""Follow-up date maths and a downloadable calendar reminder (.ics).

Privacy note: no personal data leaves the tool. The .ics is generated on the
fly and handed to the parent to add to their OWN device calendar, which then
reminds them at the follow-up date. We never store an email address or phone
number, and nothing is sent from a server -- so this works on the free tier and
keeps the "no PII leaves the deployment" promise intact.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta


def add_months(start: date, months: int) -> date:
    """Add whole months to a date, clamping the day to the target month length
    (so e.g. 31 Jan + 1 month -> 28/29 Feb rather than overflowing)."""
    m = start.month - 1 + months
    year = start.year + m // 12
    month = m % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)


def follow_up_date(months: int, from_date: date | None = None) -> date:
    """The recommended re-screening date, `months` from `from_date` (today by
    default)."""
    return add_months(from_date or date.today(), months)


def _ics_escape(text: str) -> str:
    # Order matters: escape backslashes first.
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build_ics(*, summary: str, description: str, on_date: date, uid: str) -> bytes:
    """A minimal, valid single-event VCALENDAR for a timed reminder (09:00 local
    on `on_date`) with a display alarm 15 minutes before. Returned as UTF-8 bytes
    ready to hand to st.download_button.

    Floating local time is used deliberately: the parent's own device applies its
    local timezone, which is what we want for a personal reminder.
    """
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    start = on_date.strftime("%Y%m%dT090000")
    end = (datetime.combine(on_date, datetime.min.time()) + timedelta(hours=9, minutes=30)).strftime(
        "%Y%m%dT%H%M%S"
    )
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ADHD Screening Tool//Follow-up Reminder//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{start}",
        f"DTEND:{end}",
        f"SUMMARY:{_ics_escape(summary)}",
        f"DESCRIPTION:{_ics_escape(description)}",
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        f"DESCRIPTION:{_ics_escape(summary)}",
        "TRIGGER:-PT15M",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")
