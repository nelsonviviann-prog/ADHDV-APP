"""Follow-up date maths for the re-screening plan.

No personal data, no calendar files, nothing sent: this only computes the
recommended re-check dates shown in the on-screen result and the printed PDF.
Kept separate from scoring so the date logic is easy to test.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date


def add_months(start: date, months: int) -> date:
    """Add whole months to a date, clamping the day to the target month length
    (so e.g. 31 Jan + 1 month -> 28/29 Feb rather than overflowing)."""
    m = start.month - 1 + months
    year = start.year + m // 12
    month = m % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)


def follow_up_date(months: int, from_date: date | None = None) -> date:
    """The recommended re-check date, `months` from `from_date` (today by
    default)."""
    return add_months(from_date or date.today(), months)
