import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.i18n import t, SUPPORTED_LANGUAGES, TRANSLATIONS


def test_supported_languages_not_empty():
    assert len(SUPPORTED_LANGUAGES) >= 3


def test_all_languages_have_translation_dict():
    for lang_code in SUPPORTED_LANGUAGES.values():
        assert lang_code in TRANSLATIONS


def test_translate_known_key_english():
    result = t("nav_ai_assistant", "en")
    assert result == "AI Assistant"


def test_translate_known_key_spanish():
    result = t("nav_ai_assistant", "es")
    assert result == "Asistente IA"


def test_translate_unknown_language_falls_back_to_english():
    result = t("nav_ai_assistant", "zz")  # not a real language code
    assert result == "AI Assistant"


def test_translate_unknown_key_returns_key_itself():
    result = t("nonexistent_key_xyz", "en")
    assert result == "nonexistent_key_xyz"


def test_all_core_keys_present_in_every_language():
    core_keys = ["app_title", "nav_ai_assistant", "nav_emergency", "sos_button"]
    for lang_code in TRANSLATIONS:
        for key in core_keys:
            assert key in TRANSLATIONS[lang_code], f"Missing '{key}' in '{lang_code}'"
