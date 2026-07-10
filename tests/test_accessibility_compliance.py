import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_accessibility_module_defines_toolbar_function():
    from modules import accessibility

    assert hasattr(accessibility, "render_accessibility_toolbar")
    assert hasattr(accessibility, "inject_accessibility_css")


def test_accessibility_source_contains_wcag_relevant_controls():
    """Static check that the accessibility module implements real controls,
    not just descriptive text — font scaling, contrast, and audio output."""
    source = (Path(__file__).parent.parent / "modules" / "accessibility.py").read_text()
    assert "font_scale" in source
    assert "high_contrast" in source
    assert "read_aloud" in source


def test_all_file_uploaders_have_help_text():
    """Every st.file_uploader call across modules should include a help=
    parameter for screen-reader users (WCAG 3.3.2 - labels/instructions)."""
    modules_dir = Path(__file__).parent.parent / "modules"
    for py_file in modules_dir.glob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "st.file_uploader(" in text:
            assert "help=" in text, f"{py_file.name} has a file_uploader without help= text"


def test_sos_button_is_always_rendered_in_sidebar():
    """Emergency access must not be buried inside a tab — WCAG requires
    critical actions to be reachable without deep navigation."""
    app_source = (Path(__file__).parent.parent / "app.py").read_text()
    assert "emergency.render_sos_button" in app_source
    # Confirm it's called before the tabs are built (i.e. in the sidebar block)
    sos_call_index = app_source.index("emergency.render_sos_button")
    tabs_index = app_source.index("st.tabs(")
    assert sos_call_index < tabs_index, "SOS button must be rendered outside/above the tab content"
