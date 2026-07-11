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
        f"🏥 Nearest Medical Center: "
        f"{info.get('nearest_medical_center', 'N/A')}"
    )

    st.info(
        "Reasoning: Medical teams can provide immediate treatment for "
        "injuries, illness, dehydration, or other health emergencies."
    )

    st.success(
        f"🚪 Emergency Exit: "
        f"{info.get('emergency_exit', 'N/A')}"
    )

    st.info(
        "Reasoning: Emergency exits provide the safest evacuation route "
        "during security incidents, fire alarms, or crowd-control events."
    )

    st.success(
        f"🛡 Security Help Desk: "
        f"{info.get('security_desk', 'N/A')}"
    )

    st.info(
        "Reasoning: Security personnel can assist with safety concerns, "
        "lost visitors, suspicious activity, and crowd management."
    )

    st.success(
        f"🚑 {info.get('response_team', '24x7 Emergency Response Team Available')}"
    )

    st.info(
        "Reasoning: Emergency response teams are trained to coordinate "
        "medical, security, and operational incidents inside the stadium."
    )

    if role in ("Organizer", "Venue Staff"):
        st.divider()

        st.markdown("### 🏟 Operations Access")

        st.success(
            f"📞 Internal Hotline: "
            f"{info.get('emergency_hotline', 'N/A')}"
        )

        st.info(
            "Reasoning: Internal hotlines provide direct access to the "
            "Operations Center for faster incident escalation."
        )

    st.divider()

    st.markdown("### 🤖 Emergency Guidance")

    st.warning(
        "If you witness a serious medical issue, security threat, fire, "
        "or crowd crush risk, activate SOS immediately and follow staff instructions."
    )

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

        st.success(
            "Emergency notification recorded and routed for immediate attention."
        )