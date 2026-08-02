"""Smoke tests for the Streamlit research-platform interface."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def test_landing_page_loads_without_runtime_errors() -> None:
    """The public Landing Page should load as the first application view."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    assert not app.exception
    assert any("OpenPreEduLab" in item.value for item in app.markdown)
    assert "Launch Platform" in [button.label for button in app.button]


def test_launch_platform_enters_research_workspace() -> None:
    """Launch Platform should provide a working Dashboard transition."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)

    assert not app.exception
    content = "\n".join(item.value for item in app.markdown)
    assert "Welcome back." in content
    assert "Workflow" in app.radio[0].options
    assert "Inclusive Support" in app.radio[0].options
    assert "Teacher Development" in app.radio[0].options
