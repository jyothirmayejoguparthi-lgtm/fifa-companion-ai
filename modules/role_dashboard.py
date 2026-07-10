import streamlit as st
from datetime import datetime

# Simple in-memory demo data per role. In production this would come from
# a real ops backend; kept local here to stay within a 1-day build scope.
VOLUNTEER_TASKS = [
    {"task": "Gate B crowd control support", "time": "10:00 - 12:00", "status": "Pending"},
    {"task": "Assist accessible seating Section 22", "time": "12:00 - 14:00", "status": "Pending"},
    {"task": "Lost & found desk coverage", "time": "14:00 - 16:00", "status": "Pending"},
]

ORGANIZER_ALERTS = [
    {"level": "High", "message": "Gate A crowd density above threshold"},
    {"level": "Medium", "message": "Medical center Section 30 low on supplies"},
    {"level": "Low", "message": "Parking Lot C nearing capacity"},
]

STAFF_SHIFTS = [
    {"name": "Security Team A", "zone": "Gate A - Gate B", "shift": "08:00 - 16:00"},
    {"name": "Medical Team", "zone": "Section 18 - Section 30", "shift": "24x7 rotating"},
    {"name": "Cleaning Crew", "zone": "Concourse Level 1", "shift": "06:00 - 14:00"},
]


def render(role: str, lang: str):
    """Renders a role-specific operational panel above the shared tabs."""
    if role == "Fan":
        return  # Fans use the shared tabs directly, no extra dashboard needed

    st.markdown(f"### 🧭 {role} Dashboard")

    if role == "Volunteer":
        _render_volunteer()
    elif role == "Organizer":
        _render_organizer()
    elif role == "Venue Staff":
        _render_staff()

    st.divider()


def _render_volunteer():
    st.caption("Your assigned tasks for today")
    for i, item in enumerate(VOLUNTEER_TASKS):
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.write(item["task"])
        col2.write(item["time"])
        done = col3.checkbox("Done", key=f"vol_task_{i}", value=(item["status"] == "Done"))
        if done:
            VOLUNTEER_TASKS[i]["status"] = "Done"


def _render_organizer():
    st.caption("Live operational alerts")
    for alert in ORGANIZER_ALERTS:
        icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(alert["level"], "⚪")
        st.write(f"{icon} **{alert['level']}** — {alert['message']}")


def _render_staff():
    st.caption("Today's shift roster")
    for shift in STAFF_SHIFTS:
        st.write(f"**{shift['name']}** — {shift['zone']} — {shift['shift']}")
    st.caption(f"Last synced: {datetime.now().strftime('%H:%M:%S')}")
