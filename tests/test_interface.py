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
    assert "Inclusive Education" in app.radio[0].options
    assert "Teacher Development" in app.radio[0].options


def test_ai_interpretation_page_renders_external_provider_boundary() -> None:
    """The optional DeepSeek path must render without contacting a provider."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)
    app.radio[0].set_value("AI Interpretation").run(timeout=60)

    assert not app.exception
    content = "\n".join(item.value for item in app.markdown)
    assert "Optional DeepSeek interpretation" in content
    assert "external service" in content
    assert len(app.get("download_button")) >= 1


def test_inclusive_support_page_renders_non_diagnostic_design_boundary() -> None:
    """Inclusive Support must remain a transparent, non-personal design page."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)
    app.radio[1].set_value("Upload CSV").run(timeout=60)
    assert len(app.get("file_uploader")) == 1
    app.radio[0].set_value("Inclusive Support").run(timeout=60)

    assert not app.exception
    assert len(app.get("file_uploader")) == 0
    content = "\n".join(item.value for item in app.markdown)
    assert "Inclusive education support" in content
    assert "does not assess children" in content
    assert "No child, family, teacher, or case data" in content


def test_inclusive_education_dashboard_renders_research_pathway() -> None:
    """The complete inclusive module should load with synthetic data and boundaries."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)
    app.radio[0].set_value("Inclusive Education").run(timeout=60)

    assert not app.exception
    content = "\n".join(item.value for item in app.markdown)
    assert "From Resources to Participation" in content
    assert "Policy → Resources → Practices → Child Participation → Equity" in content
    assert "not a child assessment" in content
    assert "Research Question Candidates" in content
    assert len(app.get("download_button")) >= 4

def test_reports_page_offers_markdown_word_and_pdf_downloads() -> None:
    """Users should be able to choose a familiar report-download format."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)
    app.radio[0].set_value("Reports").run(timeout=60)

    assert not app.exception
    assert app.selectbox[0].options == ["Markdown (.md)", "Word document (.docx)", "PDF document (.pdf)"]
    assert len(app.get("download_button")) >= 1


def test_all_dashboard_routes_load_without_runtime_errors() -> None:
    """Every current navigation route should survive a major interface change."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)
    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)

    navigation = next(radio for radio in app.radio if radio.label == "Workflow navigation")
    routes = list(navigation.options)
    for route in routes:
        navigation = next(radio for radio in app.radio if radio.label == "Workflow navigation")
        navigation.set_value(route).run(timeout=60)
        assert not app.exception, f"Dashboard route failed: {route}"
