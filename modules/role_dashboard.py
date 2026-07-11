import streamlit as st
from datetime import datetime

# Demo operational data
VOLUNTEER_TASKS = [
    {
        "task": "Gate B crowd control support",
        "time": "10:00 - 12:00",
        "status": "Pending",
        "priority": "High",
    },
    {
        "task": "Assist accessible seating Section 22",
        "time": "12:00 - 14:00",
        "status": "Pending",
        "priority": "Medium",
    },
    {
        "task": "Lost & found desk coverage",
        "time": "14:00 - 16:00",
        "status": "Pending",
        "priority": "Low",
    },
]

ORGANIZER_ALERTS = [
    {
        "level": "High",
        "message": "Gate A crowd density above threshold",
        "recommendation": "Reallocate volunteers to Gate A.",
    },
    {
        "level": "Medium",
        "message": "Medical center Section 30 low on supplies",
        "recommendation": "Prepare replenishment before peak attendance.",
    },
    {
        "level": "Low",
        "message": "Parking Lot C nearing capacity",
        "recommendation": "Encourage public transportation usage.",
    },
]

STAFF_SHIFTS = [
    {
        "name": "Security Team A",
        "zone": "Gate A - Gate B",
        "shift": "08:00 - 16:00",
    },
    {
        "name": "Medical Team",
        "zone": "Section 18 - Section 30",
        "shift": "24x7 rotating",
    },
    {
        "name": "Cleaning Crew",
        "zone": "Concourse Level 1",
        "shift": "06:00 - 14:00",
    },
]


def render(role: str, lang: str):
    """Render role-specific operational dashboard."""

    if role == "Fan":
        return

    st.markdown(f"### 🧭 {role} Dashboard")

    if role == "Volunteer":
        _render_volunteer()

    elif role == "Organizer":
        _render_organizer()

    elif role == "Venue Staff":
        _render_staff()

    st.divider()


def _render_volunteer():
    st.caption("Today's volunteer assignments")

    st.info(
        "AI Recommendation: Prioritize high-priority crowd-management tasks "
        "first because they have the greatest impact on visitor flow and safety."
    )

    for i, item in enumerate(VOLUNTEER_TASKS):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        col1.write(item["task"])
        col2.write(item["time"])
        col3.write(item["priority"])

        done = col4.checkbox(
            "Done",
            key=f"vol_task_{i}",
            value=(item["status"] == "Done"),
        )

        if done:
            VOLUNTEER_TASKS[i]["status"] = "Done"


def _render_organizer():
    st.caption("Live operational alerts")

    for alert in ORGANIZER_ALERTS:
        icon = {
            "High": "🔴",
            "Medium": "🟡",
            "Low": "🟢",
        }.get(alert["level"], "⚪")

        st.write(
            f"{icon} **{alert['level']}** — {alert['message']}"
        )

        st.info(
            f"Recommended Action: {alert['recommendation']}"
        )

    st.success(
        "AI Insight: Current operational focus should remain on crowd "
        "management because high-density gate conditions can create "
        "downstream delays across multiple stadium services."
    )


def _render_staff():
    st.caption("Today's shift roster")

    for shift in STAFF_SHIFTS:
        st.write(
            f"**{shift['name']}** — "
            f"{shift['zone']} — "
            f"{shift['shift']}"
        )

    st.info(
        "AI Recommendation: Verify coverage at high-traffic stadium "
        "zones before peak arrival periods to reduce incident response times."
    )

    st.caption(
        f"Last synced: {datetime.now().strftime('%H:%M:%S')}"
    )