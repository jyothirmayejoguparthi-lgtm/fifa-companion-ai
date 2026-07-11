import streamlit as st

from utils.cache_utils import get_transportation
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("Transportation")
def render(lang: str):
    st.markdown(f"### 🚌 {t('nav_transportation', lang)}")

    info = get_transportation()

    if not info:
        st.warning(
            "Transportation information is currently unavailable."
        )
        return

    # Fan-friendly recommendation section
    st.success(
        "🎯 Recommended Transport Option: Metro"
    )

    st.info(
        "Why? Public transport helps reduce congestion around the stadium, "
        "avoids parking delays, and typically provides the fastest arrival "
        "and departure experience during major events."
    )

    st.divider()

    # Metro
    metro = info.get("metro", {})

    if metro.get("available"):
        st.markdown("### 🚇 Metro")

        st.success(
            f"Nearest Station: {metro.get('nearest_station')} "
            f"({metro.get('walk_minutes')} min walk)"
        )

        st.info(
            "Reasoning: Metro services avoid road congestion and provide "
            "a predictable travel time during peak match traffic."
        )

    # Bus
    bus = info.get("bus", {})

    if bus.get("available"):
        routes = ", ".join(
            bus.get("routes", [])
        )

        st.markdown("### 🚌 Bus")

        st.success(
            f"Routes: {routes}"
        )

        st.write(
            f"Drop-off Point: {bus.get('drop_point')}"
        )

        st.info(
            "Reasoning: Bus services are useful for visitors arriving "
            "from surrounding districts and offer direct stadium access."
        )

    # Taxi
    taxi = info.get("taxi_pickup", {})

    if taxi.get("available"):
        st.markdown("### 🚕 Taxi")

        st.success(
            f"Pickup Zone: {taxi.get('location')}"
        )

        st.info(
            "Reasoning: Taxi services provide flexible transport for "
            "visitors carrying luggage or requiring direct drop-off."
        )

    # Rideshare
    rideshare = info.get("rideshare", {})

    if rideshare.get("available"):
        st.markdown("### 🚗 Ride Sharing")

        st.success(
            f"Pickup Location: {rideshare.get('location')}"
        )

        st.info(
            "Reasoning: Ride sharing is often more convenient than "
            "private parking and can reduce vehicle congestion."
        )

    # Parking
    parking = info.get("parking", {})

    if parking.get("available"):
        lots = ", ".join(
            parking.get("lots", [])
        )

        st.markdown("### 🅿️ Parking")

        st.success(
            f"Available Lots: {lots}"
        )

        st.warning(
            "Reasoning: Parking is available, but visitors may "
            "experience delays during peak arrival and departure periods."
        )

    st.divider()

    st.markdown("### 🤖 AI Travel Guidance")

    st.caption(
        "Recommended order during major match days:"
    )

    st.write(
        "1. Metro 🚇\n"
        "2. Bus 🚌\n"
        "3. Ride Share 🚗\n"
        "4. Taxi 🚕\n"
        "5. Private Parking 🅿️"
    )

    st.info(
        "This recommendation is based on congestion reduction, "
        "travel predictability, and crowd-management best practices."
    )