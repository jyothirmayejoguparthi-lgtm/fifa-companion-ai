"""
LLM client wrapper.

Design goals:
- Real GenAI call (Anthropic API) when ANTHROPIC_API_KEY is available.
- Graceful, deterministic fallback (grounded in stadium_facts.json) when the
  API key is missing or the call fails, so the app NEVER crashes and always
  gives a useful answer during a live demo.
- Caching via st.cache_data so repeated identical questions don't re-hit the API.
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
    """Load and cache the grounding knowledge base."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load stadium_facts.json: {e}")
        return {}


def _build_system_prompt(role: str, lang_name: str) -> str:
    facts = load_stadium_facts()
    return (
        "You are the Smart Stadium Assistant for FIFA World Cup 2026. "
        f"You are speaking with a stadium {role}. "
        f"Respond in {lang_name}. Keep answers short (1-3 sentences), "
        "practical, and friendly. Only use the following verified stadium "
        "data as your source of truth, do not invent facts outside it:\n\n"
        f"{json.dumps(facts, ensure_ascii=False)}"
    )


def _offline_fallback(question: str) -> str:
    """
    Deterministic keyword-matching fallback used when no API key is set
    or the API call fails. Ensures the app is always demoable offline.
    """
    facts = load_stadium_facts()
    q = question.lower()

    if "washroom" in q or "toilet" in q or "restroom" in q:
        w = facts.get("washrooms", [{}])[0]
        return f"Nearest washroom is {w.get('location', 'near the main concourse')}."
    if "medical" in q or "doctor" in q or "hurt" in q or "injur" in q:
        m = facts.get("medical_centers", [{}])[0]
        return f"Nearest medical center is at {m.get('location', 'Section 18')}, open {m.get('hours', '24x7')}."
    if "exit" in q:
        return f"Nearest emergency exit is {facts.get('emergency', {}).get('emergency_exit', 'Gate D')}."
    if "parking" in q:
        lots = ", ".join(facts.get("transportation", {}).get("parking", {}).get("lots", []))
        return f"Parking is available at: {lots}."
    if "wheelchair" in q or "accessible" in q or "elevator" in q:
        routes = ", ".join(facts.get("accessibility", {}).get("wheelchair_routes", []))
        return f"Wheelchair accessible routes: {routes}."
    if "gate" in q or "crowd" in q or "entry" in q:
        gates = facts.get("gates", [])
        low = min(gates, key=lambda g: g.get("wait_minutes", 99), default={})
        return f"Least crowded gate right now is {low.get('id', 'Gate C')} (~{low.get('wait_minutes', '?')} min wait)."
    if "metro" in q or "bus" in q or "transport" in q:
        return "Metro and bus services are both available; nearest metro station is a 5 min walk from the stadium."

    return (
        "I can help with washrooms, medical centers, gates, transportation, "
        "parking, and accessibility. Could you rephrase your question?"
    )


@st.cache_data(show_spinner=False, ttl=600)
def ask_assistant(question: str, role: str = "Fan", lang_name: str = "English") -> str:
    """
    Main entry point used by modules/ai_assistant.py.
    Cached for 10 minutes per (question, role, lang) combination to reduce
    redundant API calls (Efficiency).
    """
    if not question or not question.strip():
        return "Please enter a question."

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        logger.info("No API key found, using offline fallback.")
        return _offline_fallback(question)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        system_prompt = _build_system_prompt(role, lang_name)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": question}],
        )
        return response.content[0].text.strip()

    except Exception as e:
        logger.error(f"LLM call failed, falling back to offline mode: {e}")
        return _offline_fallback(question)
