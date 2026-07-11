import streamlit as st

from utils.cache_utils import get_accessibility_info
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("Accessibility")
def render(lang: str):
    st.markdown(f"### ♿ {t('nav_accessibility', lang)}")

    st.info(
        "This app supports adjustable text size, high-contrast mode, "
        "and read-aloud responses. Accessibility controls remain "
        "available from the sidebar throughout the experience."
    )

    info = get_accessibility_info()

    if not info:
        st.warning(
            "Accessibility information is currently unavailable."
        )
        return

    st.success(
        "🤖 Accessibility Recommendation: Use Read-Aloud mode if you "
        "prefer spoken guidance or are navigating in an unfamiliar language."
    )

    st.info(
        "Reasoning: International visitors may face language barriers "
        "or difficulty reading information while moving through crowded areas."
    )

    sections = [
        (
            "Wheelchair Accessible Routes",
            info.get("wheelchair_routes", []),
            "These routes provide step-free movement throughout the stadium."
        ),
        (
            "Elevator Access",
            info.get("elevators", []),
            "Elevators provide accessible movement between stadium levels."
        ),
        (
            "Accessible Seating",
            info.get("accessible_seating", []),
            "These seating areas are designed for wheelchair users and companions."
        ),
        (
            "Dedicated Assistance Desks",
            info.get("assistance_desks", []),
            "Staff at these locations can provide accessibility support."
        ),
    ]

    for title, items, explanation in sections:
        st.markdown(f"### {title}")

        if items:
            for item in items:
                st.markdown(f"- {item}")

            st.info(f"Reasoning: {explanation}")

        else:
            st.caption("No data available.")

        st.write("")

    sensory = info.get("sensory_room", {})

    if sensory:
        st.success(
            f"Sensory-friendly quiet room available: "
            f"{sensory.get('location')} "
            f"({sensory.get('hours')})"
        )

        st.info(
            "Reasoning: Sensory rooms provide a quieter environment for "
            "visitors who may experience sensory overload during large events."
        )


def render_accessibility_toolbar(lang: str):
    """
    Renders the always-visible accessibility controls.
    These controls actively modify the user experience.
    """

    st.sidebar.markdown("#### ♿ Accessibility Controls")

    st.session_state.font_scale = st.sidebar.slider(
        t("font_size", lang),
        min_value=0.8,
        max_value=1.8,
        value=st.session_state.get("font_scale", 1.0),
        step=0.1,
        help="Increase or decrease text size across the entire application.",
    )

    st.session_state.high_contrast = st.sidebar.toggle(
        t("high_contrast", lang),
        value=st.session_state.get("high_contrast", False),
        help="Enable a high-contrast color scheme for improved readability.",
    )

    st.session_state.read_aloud = st.sidebar.toggle(
        t("read_aloud", lang),
        value=st.session_state.get("read_aloud", False),
        help="Automatically read AI Assistant responses aloud using your browser's speech engine.",
    )


def inject_accessibility_css():
    """Apply font scaling and high-contrast styling globally."""

    scale = st.session_state.get("font_scale", 1.0)
    high_contrast = st.session_state.get("high_contrast", False)

    contrast_css = ""

    if high_contrast:
        contrast_css = """
            body,
            .stApp {
                background-color: #000000 !important;
                color: #FFFF00 !important;
            }

            .stButton > button {
                background-color: #FFFF00 !important;
                color: #000000 !important;
                border: 2px solid #FFFF00 !important;
            }

            a {
                color: #00FFFF !important;
            }
        """

    st.markdown(
        f"""
        <style>
        html {{
            font-size: {scale * 100}% !important;
        }}

        {contrast_css}
        </style>
        """,
        unsafe_allow_html=True,
    )