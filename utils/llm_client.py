"""
LLM client wrapper.

Uses Gemini text model for:
- Multilingual AI Assistant
- Context-aware stadium guidance
- Explainable recommendations

Falls back safely to deterministic stadium facts if Gemini is unavailable.
"""

import os
import json
import logging
from pathlib import Path

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_client")

DATA_PATH = Path(__file__).parent.parent / "data" / "stadium_facts.json"


@st.cache_data(show_spinner=False)
def load_stadium_facts() -> dict:
    """Load and cache stadium grounding data."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load stadium_facts.json: {e}")
        return {}


def _build_system_prompt(role: str) -> str:
    facts = load_stadium_facts()

    return f"""
You are FIFA Companion AI, a Smart Stadium Assistant for FIFA World Cup 2026.

Current user role:
{role}

Your primary goal is helping fans navigate stadiums safely and efficiently.

Instructions:
1. Detect the language of the user's question automatically.
2. Always answer in the SAME language as the user.
3. Keep responses short, practical, and friendly.
4. If giving advice or recommendations, explain WHY.
5. Use only the verified stadium information below.
6. Do not invent facts.
7. When recommending a gate, route, transport option, accessibility service, or emergency action, provide reasoning.
8. Focus on real-world stadium situations.
9. Provide actionable recommendations that help the user make a decision.
10. When possible, explain the tradeoff between available options.

Verified Stadium Data:
{json.dumps(facts, ensure_ascii=False)}

Response Style:
- Direct
- Helpful
- Explainable
- Stadium-focused
- Action-oriented
"""
    

def _offline_fallback(question: str) -> str:
    """
    Deterministic fallback used when Gemini is unavailable.
    Keeps the application fully functional during demos.
    """
    facts = load_stadium_facts()
    q = question.lower()

    if "washroom" in q or "toilet" in q or "restroom" in q:
        w = facts.get("washrooms", [{}])[0]
        return (
            f"Nearest washroom is {w.get('location', 'near the main concourse')}. "
            f"I recommend this location because it is the closest available facility."
        )

    if "medical" in q or "doctor" in q or "hurt" in q or "injur" in q:
        m = facts.get("medical_centers", [{}])[0]
        return (
            f"Nearest medical center is at "
            f"{m.get('location', 'Section 18')} "
            f"and is open {m.get('hours', '24x7')}."
        )

    if "exit" in q:
        return (
            f"Nearest emergency exit is "
            f"{facts.get('emergency', {}).get('emergency_exit', 'Gate D')}."
        )

    if "parking" in q:
        lots = ", ".join(
            facts.get("transportation", {})
            .get("parking", {})
            .get("lots", [])
        )
        return f"Parking is available at: {lots}."

    if "wheelchair" in q or "accessible" in q or "elevator" in q:
        routes = ", ".join(
            facts.get("accessibility", {})
            .get("wheelchair_routes", [])
        )
        return (
            f"Recommended wheelchair-accessible routes: {routes}. "
            f"I recommend these because they provide step-free access."
        )

    if "gate" in q or "crowd" in q or "entry" in q:
        gates = facts.get("gates", [])

        low = min(
            gates,
            key=lambda g: g.get("wait_minutes", 99),
            default={}
        )

        return (
            f"Least crowded gate right now is "
            f"{low.get('id', 'Gate C')} "
            f"(~{low.get('wait_minutes', '?')} minute wait). "
            f"I recommend this gate because it currently has the shortest wait time."
        )

    if "metro" in q or "bus" in q or "transport" in q:
        return (
            "Metro and bus services are available. "
            "The nearest metro station is approximately a 5-minute walk from the stadium."
        )

    return (
        "I can help with gates, transportation, accessibility, "
        "medical assistance, emergency services, parking, and stadium navigation."
    )


@st.cache_data(show_spinner=False, ttl=600)
def ask_assistant(
    question: str,
    role: str = "Fan",
    lang_name: str = "English",
) -> str:
    """
    Main AI Assistant entry point.

    Uses Gemini text model with:
    - Automatic language detection
    - Explainable recommendations
    - Stadium grounding

    Falls back safely if Gemini is unavailable.
    """

    if not question or not question.strip():
        return "Please enter a question."

    api_key = (
        st.secrets.get("GEMINI_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )

    if not api_key:
        logger.info("No Gemini key found, using offline fallback.")
        return _offline_fallback(question)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
{_build_system_prompt(role)}

User Question:
{question}
"""

        response = model.generate_content(prompt)

        if response and getattr(response, "text", None):
            return response.text.strip()

        logger.warning("Gemini returned empty response.")
        return _offline_fallback(question)

    except Exception as e:
        logger.error(f"Gemini text call failed: {e}")
        return _offline_fallback(question)