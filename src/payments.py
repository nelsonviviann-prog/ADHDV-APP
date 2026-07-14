"""
Paystack integration for paid consultations.

Streamlit has no HTTP endpoint of its own, so we cannot receive Paystack
webhooks. We do not need to. The flow is:

    1. initialize()  -- we POST to Paystack and get back a checkout URL,
                        tagged with a reference WE generated.
    2. The user pays on Paystack's own page.
    3. Paystack redirects them back to the app with ?reference=... in the URL.
    4. verify()      -- we ask Paystack, server-side, whether that reference
                        actually succeeded and for how much.

Step 4 is the security boundary. We NEVER trust the query string to mean the
user paid -- anyone can type `?reference=whatever` into the address bar. Only
Paystack's verify endpoint, called with our secret key, decides.

Test mode: use sk_test_/pk_test_ keys. Paystack gives you a real checkout page
and real verification with test cards; no money moves and no business
registration is required. Switching to production is a key swap, not a rewrite.
"""

from __future__ import annotations

import secrets as _secrets
from dataclasses import dataclass

import requests

PAYSTACK_API = "https://api.paystack.co"
TIMEOUT = 20

# Paystack works in kobo (1 NGN = 100 kobo).
DEFAULT_PRICE_KOBO = 500_000  # NGN 5,000.00


class PaymentError(RuntimeError):
    """Raised when Paystack cannot be reached or rejects the request."""


@dataclass(frozen=True)
class PaystackConfig:
    secret_key: str
    public_key: str
    price_kobo: int
    callback_url: str

    @property
    def is_test_mode(self) -> bool:
        return self.secret_key.startswith("sk_test_")

    @property
    def price_naira(self) -> float:
        return self.price_kobo / 100


def load_config(secrets_like) -> PaystackConfig | None:
    """Build config from st.secrets (or any mapping). Returns None when the
    deployment has not configured Paystack -- callers must handle that and show
    a 'payments unavailable' state rather than crashing."""
    try:
        block = secrets_like.get("paystack")
    except Exception:
        return None
    if not block:
        return None

    block = dict(block)
    secret = str(block.get("secret_key", "")).strip()
    public = str(block.get("public_key", "")).strip()
    if not secret or not public:
        return None

    return PaystackConfig(
        secret_key=secret,
        public_key=public,
        price_kobo=int(block.get("price_kobo", DEFAULT_PRICE_KOBO)),
        callback_url=str(block.get("callback_url", "http://localhost:8501/consult")).strip(),
    )


def new_reference() -> str:
    """A reference we control. Doubles as the code the requester uses to
    re-open their consultation later, so it must be unguessable."""
    return "CONSULT-" + _secrets.token_hex(5).upper()


def _headers(cfg: PaystackConfig) -> dict:
    return {
        "Authorization": f"Bearer {cfg.secret_key}",
        "Content-Type": "application/json",
    }


def initialize(cfg: PaystackConfig, *, email: str, reference: str) -> str:
    """Create a Paystack transaction and return the checkout URL to send the
    user to. `reference` is ours, so we can verify it later."""
    payload = {
        "email": email,
        "amount": cfg.price_kobo,
        "reference": reference,
        "callback_url": cfg.callback_url,
    }
    try:
        r = requests.post(
            f"{PAYSTACK_API}/transaction/initialize",
            json=payload,
            headers=_headers(cfg),
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        raise PaymentError(f"Could not reach Paystack: {exc}") from exc

    body = {}
    try:
        body = r.json()
    except ValueError:
        pass

    if r.status_code >= 400 or not body.get("status"):
        raise PaymentError(body.get("message") or f"Paystack error (HTTP {r.status_code})")

    url = (body.get("data") or {}).get("authorization_url")
    if not url:
        raise PaymentError("Paystack did not return a checkout URL.")
    return url


def verify(cfg: PaystackConfig, reference: str) -> dict:
    """Ask Paystack whether `reference` was actually paid.

    Returns a dict: {paid: bool, amount_kobo: int, status: str, raw: dict}.

    The caller MUST also check that amount_kobo matches what was supposed to be
    charged -- a reference could otherwise be replayed from a cheaper
    transaction. `paid` alone is not sufficient authorisation.
    """
    try:
        r = requests.get(
            f"{PAYSTACK_API}/transaction/verify/{reference}",
            headers=_headers(cfg),
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        raise PaymentError(f"Could not reach Paystack: {exc}") from exc

    try:
        body = r.json()
    except ValueError as exc:
        raise PaymentError("Paystack returned an unreadable response.") from exc

    if r.status_code >= 400 or not body.get("status"):
        raise PaymentError(body.get("message") or f"Paystack error (HTTP {r.status_code})")

    data = body.get("data") or {}
    status = str(data.get("status", "")).lower()
    return {
        "paid": status == "success",
        "amount_kobo": int(data.get("amount") or 0),
        "status": status,
        "raw": data,
    }


def verify_and_authorise(cfg: PaystackConfig, reference: str) -> tuple[bool, str]:
    """Full authorisation check: paid AND for the right amount.

    Returns (ok, human_readable_reason).
    """
    result = verify(cfg, reference)
    if not result["paid"]:
        return False, f"Payment not completed (Paystack says: {result['status'] or 'unknown'})."
    if result["amount_kobo"] < cfg.price_kobo:
        # Underpaid / replayed reference from a cheaper transaction.
        return False, (
            f"Amount paid (NGN {result['amount_kobo'] / 100:,.2f}) is less than the "
            f"consultation fee (NGN {cfg.price_naira:,.2f})."
        )
    return True, "Payment verified."
