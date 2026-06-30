"""Teacher screening page (Vanderbilt-style teacher form)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header, run_screening_page

header("Teacher Screening")
run_screening_page("Teacher")
