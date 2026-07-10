import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from utils.gemini_client import (
    analyze_image,
    ask_gemini_text,
    _validate_image,
    _hash_bytes,
    GeminiResult,
    MAX_IMAGE_BYTES,
    ALLOWED_MIME_TYPES,
)


def test_validate_image_rejects_empty_bytes():
    error = _validate_image(b"", "image/png")
    assert error is not None
    assert "no image" in error.lower()


def test_validate_image_rejects_oversized_file():
    fake_large_image = b"0" * (MAX_IMAGE_BYTES + 1)
    error = _validate_image(fake_large_image, "image/png")
    assert error is not None
    assert "too large" in error.lower()


def test_validate_image_rejects_unsupported_mime_type():
    error = _validate_image(b"fakebytes", "application/pdf")
    assert error is not None
    assert "unsupported" in error.lower()


def test_validate_image_accepts_supported_types():
    for mime in ALLOWED_MIME_TYPES:
        error = _validate_image(b"fakebytes", mime)
        assert error is None


def test_hash_bytes_is_deterministic():
    data = b"same image bytes"
    assert _hash_bytes(data) == _hash_bytes(data)


def test_hash_bytes_differs_for_different_input():
    assert _hash_bytes(b"image A") != _hash_bytes(b"image B")


def test_analyze_image_returns_result_on_invalid_input():
    result = analyze_image(b"", "image/png", "describe this")
    assert isinstance(result, GeminiResult)
    assert result.success is False


def test_analyze_image_never_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    try:
        result = analyze_image(b"fakebytesfakebytes", "image/png", "describe this")
    except Exception as e:
        pytest.fail(f"analyze_image raised unexpectedly: {e}")
    assert isinstance(result, GeminiResult)
    assert result.success is False
    assert result.error == "missing_api_key" or result.error == "missing_dependency"


def test_ask_gemini_text_rejects_empty_question():
    result = ask_gemini_text("")
    assert result.success is False
    assert "enter a question" in result.text.lower()


def test_ask_gemini_text_never_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    ask_gemini_text.clear()
    try:
        result = ask_gemini_text("Where is the nearest gate?")
    except Exception as e:
        pytest.fail(f"ask_gemini_text raised unexpectedly: {e}")
    assert isinstance(result, GeminiResult)
    assert result.success is False
