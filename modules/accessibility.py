import streamlit as st
from utils.cache_utils import get_accessibility_info
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("Accessibility")
def render(lang: str):
    st.markdown(f"### ♿ {t('nav_accessibility', lang)}")
    st.info(
        "This app supports adjustable text size, high-contrast mode, and "
        "read-aloud answers. Controls are in the sidebar and apply everywhere."
    )

    info = get_accessibility_info()
    if not info:
        st.warning("Accessibility information is currently unavailable.")
        return

    sections = [
        ("Wheelchair Accessible Routes", info.get("wheelchair_routes", [])),
        ("Elevator Access", info.get("elevators", [])),
        ("Accessible Seating", info.get("accessible_seating", [])),
        ("Dedicated Assistance Desks", info.get("assistance_desks", [])),
    ]

    for title, items in sections:
        st.markdown(f"**{title}**")
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.caption("No data available.")
        st.write("")

    sensory = info.get("sensory_room", {})
    if sensory:
        st.success(
            f"Sensory-friendly quiet room available: {sensory.get('location')} "
            f"({sensory.get('hours')})"
        )


def render_accessibility_toolbar(lang: str):
    """
    Renders the ALWAYS-VISIBLE accessibility controls in the sidebar.
    These actually change app behaviour (font scale, contrast, TTS),
    unlike a page that only describes accessibility.
    """
    st.sidebar.markdown("#### ♿ Accessibility Controls")

    st.session_state.font_scale = st.sidebar.slider(
        t("font_size", lang),
        min_value=0.8,
        max_value=1.8,
        value=st.session_state.get("font_scale", 1.0),
        step=0.1,
        help="Increase or decrease text size across the whole app.",
    )

    st.session_state.high_contrast = st.sidebar.toggle(
        t("high_contrast", lang),
        value=st.session_state.get("high_contrast", False),
        help="Switch to a black/yellow high-contrast color scheme.",
    )

    st.session_state.read_aloud = st.sidebar.toggle(
        t("read_aloud", lang),
        value=st.session_state.get("read_aloud", False),
        help="Automatically read AI Assistant answers aloud using your browser's voice.",
    )


def inject_accessibility_css():
    """Applies font scale + high contrast globally via injected CSS."""
    scale = st.session_state.get("font_scale", 1.0)
    high_contrast = st.session_state.get("high_contrast", False)

    contrast_css = ""
    if high_contrast:
        contrast_css = """
            body, .stApp { background-color: #000000 !important; color: #FFFF00 !important; }
            .stButton>button { background-color: #FFFF00 !important; color: #000000 !important; border: 2px solid #FFFF00 !important; }
            a { color: #00FFFF !important; }
        """

    st.markdown(
        f"""
        <style>
        html {{ font-size: {scale * 100}% !important; }}
        {contrast_css}
        </style>
        """,
        unsafe_allow_html=True,
    )
