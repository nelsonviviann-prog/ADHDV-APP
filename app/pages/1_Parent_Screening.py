"""Parent screening page (Vanderbilt-style parent form)."""

from __future__ import annotations

import sys
from pathlib import Path

# Make `_shared` (in app/) importable from a page in app/pages/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import header, run_screening_page

header("Parent / Caregiver Screening")
run_screening_page("Parent")
