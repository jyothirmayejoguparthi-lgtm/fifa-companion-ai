import streamlit as st
from datetime import datetime

from utils.cache_utils import get_emergency_info
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("Emergency Support")
def render(role: str, lang: str):
    st.markdown(f"### 🚨 {t('nav_emergency', lang)}")

    info = get_emergency_info()

    if not info:
        st.warning("Emergency information is currently unavailable.")
        return

    st.success(
        f"Nearest Medical Center: {info.get('nearest_medical_center', 'N/A')}"
    )
    st.success(
        f"Emergency Exit: {info.get('emergency_exit', 'N/A')}"
    )
    st.success(
        f"Security Help Desk: {info.get('security_desk', 'N/A')}"
    )
    st.success(
        f"{info.get('response_team', '24x7 Emergency Response Team Available')}"
    )

    if role in ("Organizer", "Venue Staff"):
        st.info(
            f"📞 Internal hotline: {info.get('emergency_hotline', 'N/A')}"
        )

    st.divider()

    # Emergency page SOS button
    render_sos_button(lang, "page")


def render_sos_button(lang: str, key_suffix: str = "sidebar"):
    """
    Reusable SOS button.
    Uses unique keys so sidebar and page versions don't conflict.
    """

    if st.button(
        f"🔴 {t('sos_button', lang)}",
        key=f"sos_btn_{key_suffix}",
        use_container_width=True,
    ):
        st.session_state.sos_triggered_at = datetime.now().strftime("%H:%M:%S")

    if st.session_state.get("sos_triggered_at"):
        st.error(
            f"{t('sos_confirm', lang)} "
            f"(Logged at {st.session_state.sos_triggered_at})"
        )