"""
Ticket Scanner module — multimodal ticket validation for Fans and Volunteers.

A fan uploads a photo of their physical or printed digital ticket; Gemini
Vision extracts key fields, explains any detected issues, and recommends
next actions before the user reaches the gate — reducing entry-line friction
and improving stadium operations.
"""

import streamlit as st
from datetime import datetime

from utils.gemini_client import analyze_image
from utils.i18n import t


TICKET_PROMPT = """You are a stadium ticket verification assistant for FIFA World Cup 2026.

Analyze this photo of a ticket.

Respond in this EXACT format:

READABLE: [Yes/No]

GATE: [gate letter/number if visible, else "Not visible"]

SEAT_SECTION: [section if visible, else "Not visible"]

QR_CODE_PRESENT: [Yes/No]

ISSUES: [list any problems: blurry, cropped, wrong document, expired-looking, or "None"]

REASONING: [explain why you reached your conclusion based only on visible evidence]

RECOMMENDATION: [one sentence: proceed to gate / retake photo / see help desk]

Instructions:
- Be factual and concise.
- Do not guess information that is not visible.
- Explain your reasoning clearly.
- If the image is unclear, state that honestly.
"""


def render(role: str, lang: str):
    st.markdown(f"### 🎫 {t('nav_ticket', lang)}")

    st.info(
        "Upload a photo of your ticket before arriving at the gate. "
        "The AI will verify readability, identify potential issues, "
        "explain its findings, and recommend the next step."
    )

    uploaded = st.file_uploader(
        "Upload ticket photo",
        type=["png", "jpg", "jpeg", "webp"],
        key="ticket_upload",
        help="A clear photo of your printed or digital ticket, including the QR code.",
    )

    if uploaded is not None:
        st.image(uploaded, caption="Uploaded ticket", width=350)

        if st.button("Verify Ticket", key="verify_ticket_btn"):
            image_bytes = uploaded.getvalue()
            mime_type = uploaded.type or "image/jpeg"

            with st.spinner(t("loading", lang)):
                result = analyze_image(
                    image_bytes,
                    mime_type,
                    TICKET_PROMPT,
                )

            if result.success:
                st.success(result.text)

                if "ticket_log" not in st.session_state:
                    st.session_state.ticket_log = []

                # Store FULL response (not truncated)
                st.session_state.ticket_log.append(
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "result": result.text.strip(),
                    }
                )

            else:
                st.error(f"Could not verify ticket: {result.text}")

                st.caption(
                    "You can still proceed to the gate; staff can verify manually."
                )


def render_ticket_history():
    """
    Session-local ticket verification history.
    Demonstrates traceability and operational auditability.
    """

    if "ticket_log" not in st.session_state:
        return

    if len(st.session_state.ticket_log) == 0:
        return

    st.markdown("### 🎫 Ticket Verification History")

    for item in reversed(st.session_state.ticket_log):
        with st.expander(f"🕒 {item['time']}"):
            st.text(item["result"])