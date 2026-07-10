"""
Ticket Scanner module — multimodal ticket validation for Fans and Volunteers.

A fan uploads a photo of their physical or printed digital ticket; Gemini
Vision extracts key fields and flags obvious issues (blurry, wrong match,
missing QR code) before they reach the gate — reducing entry-line friction,
which ties directly to the "Crowd Status" / gate-efficiency part of the
brief.
"""

import streamlit as st
from datetime import datetime

from utils.gemini_client import analyze_image
from utils.i18n import t

TICKET_PROMPT = """You are a stadium ticket verification assistant for FIFA World Cup 2026.
Analyze this photo of a ticket. Respond in this exact format:

READABLE: [Yes/No]
GATE: [gate letter/number if visible, else "Not visible"]
SEAT_SECTION: [section if visible, else "Not visible"]
QR_CODE_PRESENT: [Yes/No]
ISSUES: [list any problems: blurry, cropped, wrong document, expired-looking, or "None"]
RECOMMENDATION: [one sentence: proceed to gate / retake photo / see help desk]

Be concise and factual. Do not guess information that isn't visible.
"""


def render(role: str, lang: str):
    st.markdown(f"### 🎫 {t('nav_ticket', lang)}")
    st.info(
        "Upload a photo of your ticket before arriving to catch issues early "
        "(blurry scan, missing QR code, wrong gate) — faster entry, shorter lines."
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
                result = analyze_image(image_bytes, mime_type, TICKET_PROMPT)

            if result.success:
                st.success(result.text)

                if "ticket_log" not in st.session_state:
                    st.session_state.ticket_log = []

                st.session_state.ticket_log.append(
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "result": result.text[:100],
                    }
                )

            else:
                st.error(f"Could not verify ticket: {result.text}")
                st.caption(
                    "You can still proceed to the gate; staff can verify manually."
                )


def render_ticket_history():
    if "ticket_log" not in st.session_state:
        return

    st.markdown("### 🎫 Ticket Verification History")

    for item in reversed(st.session_state.ticket_log):
        st.write(f"{item['time']} - {item['result']}")