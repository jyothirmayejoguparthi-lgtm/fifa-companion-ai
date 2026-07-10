import streamlit as st
from utils.cache_utils import get_transportation
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("Transportation")
def render(lang: str):
    st.markdown(f"### 🚌 {t('nav_transportation', lang)}")

    info = get_transportation()
    if not info:
        st.warning("Transportation information is currently unavailable.")
        return

    metro = info.get("metro", {})
    if metro.get("available"):
        st.success(
            f"Metro Available — {metro.get('nearest_station')} "
            f"({metro.get('walk_minutes')} min walk)"
        )

    bus = info.get("bus", {})
    if bus.get("available"):
        routes = ", ".join(bus.get("routes", []))
        st.success(f"Bus Available — Routes: {routes} | Drop point: {bus.get('drop_point')}")

    taxi = info.get("taxi_pickup", {})
    if taxi.get("available"):
        st.success(f"Taxi Pickup Zone Available — {taxi.get('location')}")

    rideshare = info.get("rideshare", {})
    if rideshare.get("available"):
        st.success(f"Ride Sharing Support Available — {rideshare.get('location')}")

    parking = info.get("parking", {})
    if parking.get("available"):
        lots = ", ".join(parking.get("lots", []))
        st.success(f"Parking Guidance Available — {lots}")
