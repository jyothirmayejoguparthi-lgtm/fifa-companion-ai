"""
Shared error-handling utilities.

Provides a single decorator used across modules so that:
1. Every module-level render function fails safely (shows a Streamlit
   error banner instead of a raw traceback / white screen).
2. Errors are logged with enough context to debug without leaking
   internals to the end user (Security: no stack traces shown in UI).
3. Behaviour is centrally testable (tests/test_error_handling.py) instead
   of re-implemented per module.
"""

import logging
import functools

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error_handling")


def safe_render(section_name: str):
    """
    Decorator for Streamlit render functions. Catches any exception raised
    while rendering a section, logs it with the section name, and shows a
    user-friendly fallback instead of crashing the whole app.

    Usage:
        @safe_render("Crowd Status")
        def render(role, lang):
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error rendering '{section_name}': {e}", exc_info=True)
                st.error(
                    f"⚠️ {section_name} is temporarily unavailable. "
                    "Please try again or contact a staff member for help."
                )
                return None

        return wrapper

    return decorator


def validate_non_empty_string(value: str, field_name: str = "input") -> str:
    """Reusable input validation used before passing user text to any
    external API call. Raises ValueError with a clear message on failure."""
    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()
