"""
Generate a per-clinician access code and print the TOML line to add to
Streamlit Cloud -> App settings -> Secrets.

Usage:
    python -m scripts.new_clinician_code "Dr. Adekoya"
    python -m scripts.new_clinician_code "Nurse Okonkwo, FNPHY"

The code is a slugified version of the clinician's name plus 6 random hex
characters, e.g. `dr-adekoya-7a3b9c`. Codes are short enough to type on a
phone, hard to guess (~16 million options per name), and visually carry the
clinician's name so they're easy to recognise in the Secrets file.

You then paste the printed TOML line into your existing [clinician_accounts]
block in Streamlit Cloud Secrets (no redeploy needed; secrets reload live).

Revoke a clinician by deleting their line from Secrets.
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys


def slugify(name: str) -> str:
    """Turn 'Dr. Adekoya, FNPHY' into 'dr-adekoya-fnphy'."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:40] or "clinician"


def generate_code(name: str) -> str:
    return f"{slugify(name)}-{secrets.token_hex(3)}"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("name", help='The clinician display name, in quotes. Example: "Dr. Adekoya"')
    args = p.parse_args()

    code = generate_code(args.name)

    print("---------------------------------------------------------------------")
    print(f"Clinician name : {args.name}")
    print(f"Access code    : {code}")
    print("---------------------------------------------------------------------")
    print()
    print("Add THIS LINE to Streamlit Cloud -> App settings -> Secrets,")
    print("inside the [clinician_accounts] block (create the block if it")
    print("doesn't exist yet):")
    print()
    print("[clinician_accounts]")
    print(f'"{code}" = "{args.name}"')
    print()
    print("Then send the access code to the clinician via WhatsApp / SMS / email.")
    print("They enter it at the 'Clinician access code' field on the Home page.")
    print()
    print("To revoke later: delete that line from Secrets, click Save.")
    return 0


if __name__ == "__main__":
    sys.exit(main())