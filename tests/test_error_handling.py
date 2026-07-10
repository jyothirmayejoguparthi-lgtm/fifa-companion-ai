import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from utils.error_handling import safe_render, validate_non_empty_string


def test_safe_render_passes_through_normal_return_value():
    @safe_render("Test Section")
    def working_function(x):
        return x * 2

    assert working_function(5) == 10


def test_safe_render_catches_exception_and_returns_none():
    @safe_render("Test Section")
    def broken_function():
        raise RuntimeError("simulated failure")

    # Must not raise — safe_render should swallow it
    result = broken_function()
    assert result is None


def test_safe_render_preserves_function_name():
    @safe_render("Test Section")
    def my_named_function():
        return "ok"

    assert my_named_function.__name__ == "my_named_function"


def test_validate_non_empty_string_accepts_valid_input():
    result = validate_non_empty_string("  hello  ", "test_field")
    assert result == "hello"


def test_validate_non_empty_string_rejects_empty_string():
    with pytest.raises(ValueError):
        validate_non_empty_string("", "test_field")


def test_validate_non_empty_string_rejects_whitespace_only():
    with pytest.raises(ValueError):
        validate_non_empty_string("     ", "test_field")


def test_validate_non_empty_string_rejects_none():
    with pytest.raises(ValueError):
        validate_non_empty_string(None, "test_field")


def test_validate_non_empty_string_rejects_non_string_type():
    with pytest.raises(ValueError):
        validate_non_empty_string(12345, "test_field")
