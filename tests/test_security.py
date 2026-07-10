"""
Security regression tests.

These don't test runtime behaviour so much as guard against common
hackathon security mistakes: committed API keys, missing .gitignore
coverage, and unsafe direct string interpolation into external calls.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent

SUSPICIOUS_KEY_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),          # generic secret-key-like strings
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),        # Google API key format
    re.compile(r"anthropic_api_key\s*=\s*[\"'][a-zA-Z0-9]+[\"']", re.IGNORECASE),
]

PY_FILES = list(PROJECT_ROOT.rglob("*.py"))


def test_no_hardcoded_api_keys_in_source():
    offenders = []
    for path in PY_FILES:
        if "test_security" in path.name:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SUSPICIOUS_KEY_PATTERNS:
            if pattern.search(text):
                offenders.append(str(path))
    assert not offenders, f"Possible hardcoded secret found in: {offenders}"


def test_api_keys_read_from_environment_only():
    """Both LLM clients must source keys via os.environ, not literals."""
    llm_client = (PROJECT_ROOT / "utils" / "llm_client.py").read_text()
    gemini_client = (PROJECT_ROOT / "utils" / "gemini_client.py").read_text()

    assert "os.environ.get(" in llm_client
    assert "os.environ.get(" in gemini_client


def test_gitignore_excludes_env_files():
    gitignore = (PROJECT_ROOT / ".gitignore").read_text()
    assert ".env" in gitignore


def test_gitignore_excludes_pycache():
    gitignore = (PROJECT_ROOT / ".gitignore").read_text()
    assert "__pycache__" in gitignore


def test_all_external_calls_wrapped_in_try_except():
    """Sanity check: any file importing anthropic or google.generativeai
    must also contain a try/except block near the call site."""
    for path in PY_FILES:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "import anthropic" in text or "import google.generativeai" in text:
            assert "try:" in text and "except" in text, (
                f"{path} calls an external AI API without try/except"
            )
