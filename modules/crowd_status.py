import streamlit as st
from utils.cache_utils import get_gates
from utils.i18n import t
from utils.error_handling import safe_render

STATUS_COLOR = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}


@safe_render("Crowd Status")
def render(role: str, lang: str):
    st.markdown(f"### 📊 {t('nav_crowd_status', lang)}")

    gates = get_gates()
    if not gates:
        st.warning("Crowd data is currently unavailable. Please check back shortly.")
        return

    for gate in gates:
        icon = STATUS_COLOR.get(gate.get("crowd_status", ""), "⚪")
        with st.container():
            st.markdown(f"#### {icon} {gate['id']}")
            st.write(f"Status: **{gate['crowd_status']} Crowd**")
            st.write(f"Recommendation: {gate['recommendation']}")

            # Organizers and staff get operational detail fans don't need
            if role in ("Organizer", "Venue Staff"):
                st.caption(f"⏱ Estimated wait: {gate.get('wait_minutes', 'N/A')} min")
            st.divider()

    if role == "Organizer":
        avg_wait = sum(g.get("wait_minutes", 0) for g in gates) / len(gates)
        st.metric("Average wait time across all gates", f"{avg_wait:.1f} min")
        high_crowd_gates = [g["id"] for g in gates if g["crowd_status"] == "High"]
        if high_crowd_gates:
            st.warning(f"⚠️ Consider reallocating staff to: {', '.join(high_crowd_gates)}")
