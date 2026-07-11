"""
Gemini API client — multimodal (text + vision) layer.

Design goals (mirrors utils/llm_client.py's reliability pattern):
- Real google-generativeai integration for text AND image inputs.
- Every external call wrapped in try/except with typed, logged failures —
  never propagates an exception to the Streamlit UI layer (Security +
  Code Quality: no unhandled exceptions leaking stack traces to users).
- API key read only from environment (Security: never hardcoded, never
  logged, never echoed back in responses).
- Caching via st.cache_data keyed on image bytes hash + prompt (Efficiency:
  avoids re-analyzing the same image on every rerun).
- Explicit input validation (file size / mime type) before any network call
  (Security: prevents oversized/unsupported payloads reaching the API).
"""

import os
import logging
import hashlib
from dataclasses import dataclass
from typing import Optional

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini_client")

MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8MB upload cap
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@dataclass
class GeminiResult:
    """Typed result object so callers don't have to guess response shape."""
    success: bool
    text: str
    error: Optional[str] = None


def _get_api_key() -> Optional[str]:
    return st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")


def _validate_image(image_bytes: bytes, mime_type: str) -> Optional[str]:
    """Returns an error string if invalid, else None."""
    if not image_bytes:
        return "No image data received."
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return f"Image too large ({len(image_bytes) / 1e6:.1f}MB). Max is 8MB."
    if mime_type not in ALLOWED_MIME_TYPES:
        return f"Unsupported file type: {mime_type}."
    return None


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@st.cache_data(show_spinner=False, ttl=600)
def _cached_vision_call(image_hash: str, image_bytes: bytes, mime_type: str, prompt: str) -> GeminiResult:
    """
    Cache is keyed on image_hash + prompt (via Streamlit's arg hashing).
    image_bytes is passed too so the actual call has the payload, but the
    hash ensures identical images don't re-trigger the API.
    """
    api_key = _get_api_key()
    if not api_key:
        return GeminiResult(
            success=False,
            text="Vision analysis unavailable: GEMINI_API_KEY is not configured.",
            error="missing_api_key",
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = model.generate_content([prompt, image_part])

        if not response or not getattr(response, "text", None):
            return GeminiResult(success=False, text="", error="empty_response")

        return GeminiResult(success=True, text=response.text.strip())

    except ImportError:
        logger.error("google-generativeai package not installed.")
        return GeminiResult(
            success=False,
            text="Vision analysis unavailable: google-generativeai package not installed.",
            error="missing_dependency",
        )
    except Exception as e:
        logger.error(f"Gemini Vision call failed: {e}")
        return GeminiResult(
            success=False,
            text="Vision analysis is temporarily unavailable. Please try again shortly.",
            error=str(e),
        )


def analyze_image(image_bytes: bytes, mime_type: str, prompt: str) -> GeminiResult:
    """
    Public entry point for all image-analysis callers. Validates input
    before touching the network/cache layer.
    """
    validation_error = _validate_image(image_bytes, mime_type)
    if validation_error:
        logger.warning(f"Image validation failed: {validation_error}")
        return GeminiResult(success=False, text=validation_error, error="validation_error")

    image_hash = _hash_bytes(image_bytes)
    return _cached_vision_call(image_hash, image_bytes, mime_type, prompt)


@st.cache_data(show_spinner=False, ttl=600)
def ask_gemini_text(question: str, context: str = "") -> GeminiResult:
    """Text-only Gemini call, used as an alternate/backup text model path."""
    if not question or not question.strip():
        return GeminiResult(success=False, text="Please enter a question.", error="empty_input")

    api_key = _get_api_key()
    if not api_key:
        return GeminiResult(success=False, text="Gemini text model unavailable: no API key.", error="missing_api_key")

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        full_prompt = f"{context}\n\nQuestion: {question}" if context else question
        response = model.generate_content(full_prompt)

        if not response or not getattr(response, "text", None):
            return GeminiResult(success=False, text="", error="empty_response")

        return GeminiResult(success=True, text=response.text.strip())

    except Exception as e:
        logger.error(f"Gemini text call failed: {e}")
        return GeminiResult(success=False, text="I couldn't process that right now. Please try again.", error=str(e))
