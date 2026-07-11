import streamlit as st

from utils.cache_utils import get_gates
from utils.i18n import t
from utils.error_handling import safe_render

STATUS_COLOR = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🔴",
}


@safe_render("Crowd Status")
def render(role: str, lang: str):
    st.markdown(f"### 📊 {t('nav_crowd_status', lang)}")

    gates = get_gates()

    if not gates:
        st.warning(
            "Crowd data is currently unavailable. Please check back shortly."
        )
        return

    least_busy_gate = min(
        gates,
        key=lambda g: g.get("wait_minutes", 999)
    )

    if role == "Fan":
        st.success(
            f"🎯 Recommended Entry Gate: {least_busy_gate['id']} "
            f"(~{least_busy_gate.get('wait_minutes', '?')} min wait)"
        )

        st.info(
            f"Why? {least_busy_gate['id']} currently has the shortest "
            f"estimated wait time and the lowest crowd density, helping "
            f"you enter the stadium faster and avoid congestion."
        )

    st.divider()

    for gate in gates:
        icon = STATUS_COLOR.get(
            gate.get("crowd_status", ""),
            "⚪"
        )

        st.markdown(f"#### {icon} {gate['id']}")

        st.write(
            f"**Current Status:** {gate['crowd_status']} Crowd"
        )

        st.write(
            f"**Recommendation:** {gate['recommendation']}"
        )

        wait_time = gate.get("wait_minutes", "N/A")

        st.write(
            f"**Estimated Wait:** {wait_time} min"
        )

        # Explainable reasoning
        if gate["id"] == least_busy_gate["id"]:
            st.success(
                f"Reasoning: {gate['id']} currently offers the fastest "
                f"entry experience because it has the shortest queue "
                f"and lowest estimated wait time."
            )

        elif gate.get("crowd_status") == "High":
            st.warning(
                f"Reasoning: {gate['id']} is experiencing high crowd "
                f"density. Visitors may experience delays and should "
                f"consider alternative gates when possible."
            )

        else:
            st.info(
                f"Reasoning: {gate['id']} remains operational but may "
                f"have moderate waiting times depending on arrival flow."
            )

        st.divider()

    # Organizer / Staff operational dashboard
    if role in ("Organizer", "Venue Staff"):

        st.markdown("### 🏟 Operations Insights")

        avg_wait = (
            sum(g.get("wait_minutes", 0) for g in gates)
            / len(gates)
        )

        st.metric(
            "Average Wait Time",
            f"{avg_wait:.1f} min"
        )

        high_crowd_gates = [
            g["id"]
            for g in gates
            if g.get("crowd_status") == "High"
        ]

        if high_crowd_gates:
            st.warning(
                "⚠️ Staff Reallocation Recommended: "
                + ", ".join(high_crowd_gates)
            )

            st.info(
                "Reasoning: These gates are currently operating "
                "under higher crowd pressure and may benefit from "
                "additional volunteers, security personnel, or "
                "entry lane management."
            )

        else:
            st.success(
                "✅ Crowd levels are currently balanced across all gates."
            )