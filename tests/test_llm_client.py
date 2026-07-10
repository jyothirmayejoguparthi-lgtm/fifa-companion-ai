"""
Tests for utils/llm_client.py

Run with: pytest tests/ -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import pytest
from utils.llm_client import ask_assistant, load_stadium_facts, _offline_fallback


def test_load_stadium_facts_returns_dict():
    facts = load_stadium_facts()
    assert isinstance(facts, dict)
    assert "gates" in facts
    assert "washrooms" in facts


def test_offline_fallback_washroom_question():
    answer = _offline_fallback("Where is the nearest washroom?")
    assert "washroom" in answer.lower() or "section" in answer.lower()


def test_offline_fallback_medical_question():
    answer = _offline_fallback("I need medical help")
    assert "medical" in answer.lower() or "section" in answer.lower()


def test_offline_fallback_gate_question():
    answer = _offline_fallback("Which gate has the shortest queue?")
    assert "gate" in answer.lower()


def test_offline_fallback_unknown_question():
    answer = _offline_fallback("What's the meaning of life?")
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_ask_assistant_empty_question_returns_prompt():
    result = ask_assistant("", role="Fan", lang_name="English")
    assert "enter a question" in result.lower()


def test_ask_assistant_never_raises_without_api_key(monkeypatch):
    """Even without an API key set, the assistant must never crash — it
    should gracefully fall back to offline mode (critical for demo reliability)."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    ask_assistant.clear()  # bust cache so this run actually executes
    try:
        result = ask_assistant("Where is the nearest gate?", role="Fan", lang_name="English")
    except Exception as e:
        pytest.fail(f"ask_assistant raised an exception unexpectedly: {e}")
    assert isinstance(result, str)
    assert len(result) > 0


def test_ask_assistant_handles_broken_api_key_gracefully(monkeypatch):
    """If an invalid API key is set, the call should fail internally and
    fall back rather than propagate an exception to the UI layer."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "invalid-test-key-12345")
    ask_assistant.clear()
    try:
        result = ask_assistant("Where can I park?", role="Fan", lang_name="English")
    except Exception as e:
        pytest.fail(f"ask_assistant raised an exception unexpectedly: {e}")
    assert isinstance(result, str)
    assert len(result) > 0
