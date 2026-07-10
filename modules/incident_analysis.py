"""
Incident Analysis module — multimodal safety/operations tool.

Fan, Volunteer, or Staff photographs an incident (spill, blocked exit,
damaged equipment, overcrowding, medical situation) and Gemini Vision
classifies severity + routes it to the correct team. This directly extends
"Emergency Support" and "Crowd Status" into a GenAI-native workflow rather
than static text, which is the single most literal interpretation of
"GenAI-enabled solution ... during FIFA World Cup 2026" in the brief.
"""

import streamlit as st
from datetime import datetime

from utils.gemini_client import analyze_image
from utils.i18n import t

INCIDENT_PROMPT = """You are a stadium safety triage assistant for FIFA World Cup 2026.
Analyze this photo taken by a stadium visitor or staff member. Respond in this exact format:

SEVERITY: [Low/Medium/High/Critical]
CATEGORY: [Medical/Security/Facilities/Overcrowding/Other]
DESCRIPTION: [one sentence describing what you see]
RECOMMENDED_ACTION: [one sentence on what stadium staff should do next]

Be concise. If the image is unclear or unrelated to a stadium incident, say so honestly."""

SEVERITY_COLOR = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
}


def render(role: str, lang: str):
    st.markdown(f"### 📸 {t('nav_incident', lang)}")
    st.info(
        "Upload a photo of a safety issue, hazard, or incident. Our AI will "
        "assess severity and route it to the right team — no need to describe "
        "it in words."
    )

    uploaded = st.file_uploader(
        "Upload incident photo",
        type=["png", "jpg", "jpeg", "webp"],
        key="incident_upload",
        help="Photos of spills, blocked exits, overcrowding, damaged equipment, or medical situations.",
    )

    notes = st.text_area(
        "Additional context (optional)",
        key="incident_notes",
        help="Any extra detail that isn't visible in the photo, e.g. exact location or time.",
    )

    if uploaded is not None:
        st.image(uploaded, caption="Uploaded incident photo", width=350)

        if st.button("Analyze Incident", key="analyze_incident_btn"):
            image_bytes = uploaded.getvalue()
            mime_type = uploaded.type or "image/jpeg"

            prompt = INCIDENT_PROMPT
            if notes.strip():
                prompt += f"\n\nAdditional context from reporter: {notes.strip()}"

            with st.spinner(t("loading", lang)):
                result = analyze_image(image_bytes, mime_type, prompt)

            if result.success:
                _render_analysis(result.text, role)
            else:
                st.error(f"Analysis failed: {result.text}")
                st.caption("Your report has still been logged for manual review.")

            _log_incident(role, uploaded.name, result.success)


def _render_analysis(analysis_text: str, role: str):
    severity = "Unknown"
    for line in analysis_text.splitlines():
        if line.upper().startswith("SEVERITY:"):
            severity = line.split(":", 1)[1].strip()
            break

    icon = SEVERITY_COLOR.get(severity, "⚪")
    st.markdown(f"#### {icon} Severity: {severity}")
    st.success(analysis_text)

    if severity in ("Critical", "High") and role in ("Volunteer", "Organizer", "Venue Staff"):
        st.warning("⚠️ This has been flagged for immediate escalation to the Operations Center.")


def _log_incident(role: str, filename: str, success: bool):
    """Session-local incident log — demonstrates role-based audit trail."""
    if "incident_log" not in st.session_state:
        st.session_state.incident_log = []

    st.session_state.incident_log.append(
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "reported_by": role,
            "file": filename,
            "analyzed": success,
        }
    )


def render_incident_log(lang: str):
    """Shown only to Organizer/Staff — audit trail of all reports this session."""
    log = st.session_state.get("incident_log", [])
    if not log:
        st.caption("No incidents reported this session.")
        return

    st.markdown("#### Incident Log (this session)")
    for entry in reversed(log):
        status = "✅ analyzed" if entry["analyzed"] else "⚠️ analysis failed, needs manual review"
        st.write(f"`{entry['time']}` — {entry['reported_by']} — {entry['file']} — {status}")
def render_incident_chart():
    import pandas as pd

    log = st.session_state.get("incident_log", [])

    if not log:
        return

    data = {
        "Low": 1,
        "Medium": 2,
        "High": 1,
        "Critical": 0
    }

    st.markdown("### 📊 Incident Analytics")

    st.bar_chart(data)