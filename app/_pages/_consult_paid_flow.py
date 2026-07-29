"""
Paid live consultation with a clinician.

Flow
----
    no reference        -> intro + "start a consultation" form -> Paystack checkout
    ?reference=... back -> verify with Paystack -> unlock thread
    have a code         -> re-enter it to resume an existing thread

Security
--------
The query string is NOT trusted. `?reference=X` only tells us which reference
to ASK PAYSTACK ABOUT; payments.verify_and_authorise() is what actually decides
whether the thread unlocks. Once Paystack confirms, the DB row is marked paid
and subsequent visits trust the DB (so we do not hit the API on every rerun).

"Live" messaging
----------------
Streamlit cannot push. @st.fragment(run_every=2) re-runs ONLY the message feed
every 2 seconds, so new messages appear without the user touching anything and
without re-rendering (or resetting) the rest of the page.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _shared import (  # noqa: E402
    ROLE_CLINICIAN,
    current_role,
    header,
)
from src import database as db      # noqa: E402
from src import payments           # noqa: E402

header("Consult a Clinician")
db.init_db()

MY_ROLE = current_role() or "Parent"

# Clinicians answer consultations from their Dashboard inbox, not from here.
if MY_ROLE == ROLE_CLINICIAN:
    st.info(
        "Clinicians reply to consultations from the **Consultations** section "
        "of the Clinician Dashboard, not from this page."
    )
    st.stop()


cfg = payments.load_config(st.secrets)

# ---------------------------------------------------------------------------
# Payments not configured -- be honest rather than showing a dead button.
# ---------------------------------------------------------------------------
if cfg is None:
    st.warning(
        "**Paid consultations are not available on this deployment yet.**\n\n"
        "The deployment owner has not configured a payment provider. "
        "If you need help interpreting a screening result, take your PDF report "
        "to the referral facility listed on your result page, or leave a note on "
        "the **Feedback** page."
    )
    with st.expander("Deployment owner: how to enable this"):
        st.markdown(
            """
Add your Paystack keys to `.streamlit/secrets.toml` (local) or
**Streamlit Cloud → App settings → Secrets**:

```toml
[paystack]
secret_key   = "sk_test_xxxxxxxxxxxxxxxxx"
public_key   = "pk_test_xxxxxxxxxxxxxxxxx"
price_kobo   = 500000                      # NGN 5,000.00
callback_url = "http://localhost:8501/consult"
```

Test keys (`sk_test_` / `pk_test_`) need no business registration and move no
real money. Set `callback_url` to this page's URL on your deployment.
            """
        )
    st.stop()


# ---------------------------------------------------------------------------
# 1. Coming back from Paystack? Verify before trusting anything.
# ---------------------------------------------------------------------------
qp_reference = st.query_params.get("reference")

if qp_reference and not st.session_state.get("consult_ref"):
    consultation = db.find_consultation(qp_reference)
    if not consultation:
        st.error(
            f"No consultation found for reference `{qp_reference}`. "
            "If you were charged, contact the deployment owner with this reference."
        )
    else:
        with st.spinner("Confirming your payment with Paystack..."):
            try:
                ok, reason = payments.verify_and_authorise(cfg, qp_reference)
            except payments.PaymentError as exc:
                ok, reason = False, str(exc)

        if ok:
            db.mark_consultation_paid(qp_reference)
            st.session_state["consult_ref"] = qp_reference.strip().upper()
            st.query_params.clear()
            st.rerun()
        else:
            st.error(f"Payment could not be confirmed. {reason}")
            st.caption(
                "If money left your account, do not pay again -- contact the "
                f"deployment owner quoting `{qp_reference}`."
            )


# ---------------------------------------------------------------------------
# 2. Resolve the active consultation (from session, or a code the user enters).
# ---------------------------------------------------------------------------
active = None
ref = st.session_state.get("consult_ref")
if ref:
    active = db.find_consultation(ref)
    if not active or active["status"] == "pending":
        # Never let an unpaid row through, even if the session claims otherwise.
        active = None
        st.session_state.pop("consult_ref", None)


# ---------------------------------------------------------------------------
# 3. No active thread -> sell it.
# ---------------------------------------------------------------------------
if active is None:
    st.markdown(
        f"<div class='info-card'>"
        f"<b>Talk to a clinician about your child's screening result.</b><br>"
        f"<span style='color:#57534e;'>A verified clinician reviews your result and "
        f"answers your questions in a private chat. Messages appear live.</span><br><br>"
        f"<b style='color:#1e3a8a; font-size:20px;'>NGN {cfg.price_naira:,.0f}</b>"
        f"<span style='color:#78716c;'> &middot; one consultation</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if cfg.is_test_mode:
        st.info(
            "**Test mode.** No real money will be charged. Use Paystack's test "
            "card `4084 0840 8408 4081`, any future expiry, any CVV, OTP `123456`."
        )

    st.warning(
        "**This is not emergency care and not a diagnosis.** A consultation "
        "helps you understand a screening result and decide next steps. It does "
        "not replace an in-person evaluation by a child psychiatrist or "
        "pediatrician. If your child is in crisis, go to a hospital."
    )

    tab_new, tab_resume = st.tabs(["Start a consultation", "I already have a code"])

    with tab_new:
        with st.form("start_consult"):
            email = st.text_input(
                "Your email",
                placeholder="you@example.com",
                help="Paystack sends your receipt here. We do not use it for anything else.",
            )
            study_id = st.text_input(
                "Child Study ID (optional)",
                placeholder="ADHD-NG-XXXXXX",
                help="Share the ID from your screening so the clinician can see the result.",
            )
            pay = st.form_submit_button(
                f"Pay NGN {cfg.price_naira:,.0f} and start", type="primary",
                use_container_width=True,
            )

        if pay:
            if not email.strip() or "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                reference = payments.new_reference()
                try:
                    db.create_consultation(
                        reference=reference,
                        study_id=study_id or None,
                        requester_role=MY_ROLE,
                        requester_email=email,
                        amount_kobo=cfg.price_kobo,
                    )
                    checkout_url = payments.initialize(
                        cfg, email=email.strip(), reference=reference
                    )
                except payments.PaymentError as exc:
                    st.error(f"Could not start the payment: {exc}")
                except Exception as exc:
                    st.error(f"Could not start the payment ({type(exc).__name__}).")
                else:
                    st.success("Consultation created. Continue to payment below.")
                    st.markdown(
                        f"**Save this code:** `{reference}`  \n"
                        "You need it to re-open this consultation later."
                    )
                    st.link_button(
                        f"Continue to Paystack -- pay NGN {cfg.price_naira:,.0f}",
                        checkout_url,
                        type="primary",
                        use_container_width=True,
                    )

    with tab_resume:
        code = st.text_input("Consultation code", placeholder="CONSULT-XXXXXXXXXX")
        if st.button("Open my consultation", use_container_width=True):
            found = db.find_consultation(code)
            if not found:
                st.error("No consultation with that code.")
            elif found["status"] == "pending":
                st.warning(
                    "That consultation has not been paid for yet. If you completed "
                    "payment, wait a moment and try again."
                )
            else:
                st.session_state["consult_ref"] = found["reference"]
                st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# 4. Paid -> the live thread.
# ---------------------------------------------------------------------------
consultant = active["consultant_name"]
is_closed = active["status"] == "closed"

st.markdown(
    f"<div class='info-card' style='border-left-color:#166534;'>"
    f"<b>Consultation <code>{active['reference']}</code></b><br>"
    f"<span style='color:#57534e;'>"
    f"{'Clinician: <b>' + consultant + '</b>' if consultant else 'Waiting for a clinician to join...'}"
    f"{' &middot; <b>closed</b>' if is_closed else ''}"
    f"</span></div>",
    unsafe_allow_html=True,
)

if not consultant and not is_closed:
    st.info(
        "Your payment is confirmed. A clinician will join shortly - you can "
        "write your question now and they will see it when they open the thread."
    )


@st.fragment(run_every=2)
def message_feed(consultation_id: int, my_role: str) -> None:
    """Re-runs every 2s on its own, so the other side's replies appear without
    the reader doing anything. Only this fragment reruns, not the whole page."""
    messages = db.messages_for(consultation_id)
    if not messages:
        st.caption("No messages yet. Say hello and describe your concern.")
        return
    for m in messages:
        mine = m["sender_role"] == my_role
        who = "user" if mine else "assistant"
        label = m["sender_name"] or m["sender_role"]
        with st.chat_message(who):
            st.markdown(f"**{label}**  \n{m['body']}")
            st.caption((m["sent_at"] or "").replace("T", " "))


message_feed(active["id"], MY_ROLE)

if is_closed:
    st.info("This consultation has been closed by the clinician.")
else:
    if prompt := st.chat_input("Type your message..."):
        db.post_message(
            consultation_id=active["id"],
            sender_role=MY_ROLE,
            sender_name=MY_ROLE,
            body=prompt,
        )
        st.rerun()

with st.expander("Consultation details"):
    st.write(f"**Code:** `{active['reference']}` (keep this to re-open the thread)")
    st.write(f"**Status:** {active['status']}")
    st.write(f"**Study ID:** {active['study_id'] or '-'}")
    st.write(f"**Paid:** NGN {active['amount_kobo'] / 100:,.2f} on "
             f"{(active['paid_at'] or '-').replace('T', ' ')}")
    if st.button("Leave this consultation (you can re-open with your code)"):
        st.session_state.pop("consult_ref", None)
        st.rerun()
