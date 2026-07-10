import streamlit as st

from utils.cache_utils import init_session_state
from utils.i18n import t, SUPPORTED_LANGUAGES
from modules import (
    ai_assistant,
    crowd_status,
    accessibility,
    transportation,
    emergency,
    role_dashboard,
    incident_analysis,
    ticket_scanner,
)

st.set_page_config(
    page_title="FIFA World Cup 2026 - Smart Stadium Assistant",
    page_icon="⚽",
    layout="wide",
)

init_session_state()

# ---------- Sidebar: role, language, accessibility controls, SOS ----------
st.sidebar.markdown("## ⚽ FIFA Companion AI")

role_options = ["Fan", "Volunteer", "Organizer", "Venue Staff"]
st.session_state.role = st.sidebar.selectbox(
    t("select_role", st.session_state.lang),
    role_options,
    index=role_options.index(st.session_state.role),
    help="Switch persona to see a tailored dashboard.",
)

lang_display = st.sidebar.selectbox(
    t("select_language", st.session_state.lang),
    list(SUPPORTED_LANGUAGES.keys()),
    index=0,
    help="Changes the interface language and AI Assistant response language.",
)
st.session_state.lang = SUPPORTED_LANGUAGES[lang_display]
st.session_state.lang_name = lang_display

accessibility.render_accessibility_toolbar(st.session_state.lang)
accessibility.inject_accessibility_css()

st.sidebar.divider()
emergency.render_sos_button(st.session_state.lang, "sidebar")

# ---------- Main content ----------
lang = st.session_state.lang
role = st.session_state.role
st.markdown("""
# ⚽ FIFA Companion AI
### AI-Powered Smart Stadium Operations Platform
""")
st.caption(
    "Helping FIFA World Cup 2026 fans, volunteers, organizers and venue staff "
    "navigate stadiums, transportation, accessibility, crowd management and "
    "emergency services — powered by GenAI."
)
col1, col2, col3, col4 = st.columns(4)

col1.metric("🏟 Active Gates", "4")
col2.metric("🚨 Incidents", len(st.session_state.get("incident_log", [])))
col3.metric("👥 Crowd Alerts", "1")
col4.metric("🎫 Tickets Scanned", len(st.session_state.get("ticket_log", [])))
st.success("""
🤖 AI Systems Status

✅ Claude Assistant Online
✅ Gemini Vision Online
✅ Accessibility Active
✅ Emergency Response Active
""")
# Role-specific operational dashboard (empty for Fan)
role_dashboard.render(role, lang)

tab_labels = [
    t("nav_ai_assistant", lang),
    t("nav_crowd_status", lang),
    t("nav_accessibility", lang),
    t("nav_transportation", lang),
    t("nav_emergency", lang),
    t("nav_incident", lang),
    t("nav_ticket", lang),
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    ai_assistant.render(role, lang, st.session_state.lang_name)

with tabs[1]:
    crowd_status.render(role, lang)

with tabs[2]:
    accessibility.render(lang)

with tabs[3]:
    transportation.render(lang)

with tabs[4]:
    emergency.render(role, lang)

with tabs[5]:
    incident_analysis.render(role, lang)
    incident_analysis.render_incident_chart()
    if role in ("Organizer", "Venue Staff"):
        st.divider()
        incident_analysis.render_incident_log(lang)

with tabs[6]:
    ticket_scanner.render(role, lang)

    st.divider()

    ticket_scanner.render_ticket_history()

st.divider()
st.caption(
    "Built for Hack2Skill PromptWars Challenge 4 · FIFA World Cup 2026 "
    "Smart Stadium Assistant · Demo data, not affiliated with FIFA."
)
