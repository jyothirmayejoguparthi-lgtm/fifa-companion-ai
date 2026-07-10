"""
Small helpers around Streamlit caching used across modules to avoid
recomputation on every rerun (Efficiency scoring).
"""

import streamlit as st
from utils.llm_client import load_stadium_facts


@st.cache_data(show_spinner=False)
def get_gates():
    return load_stadium_facts().get("gates", [])


@st.cache_data(show_spinner=False)
def get_transportation():
    return load_stadium_facts().get("transportation", {})


@st.cache_data(show_spinner=False)
def get_accessibility_info():
    return load_stadium_facts().get("accessibility", {})


@st.cache_data(show_spinner=False)
def get_emergency_info():
    return load_stadium_facts().get("emergency", {})


def init_session_state():
    """Initialize all session_state keys once so widgets don't reset on rerun."""
    defaults = {
        "role": "Fan",
        "lang": "en",
        "lang_name": "English",
        "font_scale": 1.0,
        "high_contrast": False,
        "read_aloud": False,
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
