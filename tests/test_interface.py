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


def test_workspace_query_parameter_opens_sidebar_navigation() -> None:
    """A shared workspace URL should open directly with research navigation."""
    app = AppTest.from_file(str(APP_PATH))
    app.query_params["view"] = "platform"
    app.run(timeout=60)

    assert not app.exception
    navigation = next(radio for radio in app.radio if radio.label == "Workflow navigation")
    assert "Inclusive Education" in navigation.options
    assert "Workflow" in navigation.options



def test_launch_platform_enters_research_workspace() -> None:
    """Launch Platform should provide a working Dashboard transition."""
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=60)

    next(button for button in app.button if button.label == "Launch Platform").click().run(timeout=60)

    assert not app.exception
    assert app.query_params["view"] == ["platform"]
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
    content = "\n".join(
        [item.value for item in app.markdown]
        + [item.value for item in app.caption]
    )
    assert "From Resources to Participation" in content
    assert "Policy → Resources → Practices → Child Participation → Equity" in content
    assert "not a child assessment" in content
    assert "Research Question Candidates" in content
    assert "does not depend on colour alone" in content
    assert "Expert content-review materials" in content
    assert "Accessible chart data tables" in [expander.label for expander in app.expander]
    assert "Review template instructions" in [expander.label for expander in app.expander]
    assert "Upload completed expert content-review CSV" in [
        uploader.label for uploader in app.get("file_uploader")
    ]
    expander_labels = [expander.label for expander in app.expander]
    assert "Cognitive interview evidence workflow" in expander_labels
    assert "Item revision decision audit workflow" in expander_labels
    uploader_labels = [uploader.label for uploader in app.get("file_uploader")]
    assert "Upload cognitive interview record CSV" in uploader_labels
    assert "Upload item revision decision CSV" in uploader_labels
    assert "Instrument version and comparability workflow" in expander_labels
    assert "Upload instrument version registry CSV" in uploader_labels
    assert "Feasibility pilot and data-quality workflow" in expander_labels
    assert "Upload feasibility pilot CSV" in uploader_labels
    assert "Feasibility pilot response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    slider_labels = [slider.label for slider in app.slider]
    assert "Endpoint follow-up threshold" in slider_labels
    assert "Missingness follow-up threshold" in slider_labels
    assert "Reliability and repeated-administration workflow" in expander_labels
    assert "Upload reliability audit CSV" in uploader_labels
    assert "Reliability audit response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Construct structure readiness and exploratory components workflow" in expander_labels
    assert "Upload construct structure audit CSV" in uploader_labels
    assert "Construct structure audit response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download construct structure audit template" in [
        button.label for button in app.get("download_button")
    ]
    assert "Subgroup measurement comparability readiness workflow" in expander_labels
    assert "Upload subgroup comparability audit CSV" in uploader_labels
    assert "Subgroup comparability audit response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download subgroup comparability audit template" in [
        button.label for button in app.get("download_button")
    ]
    assert "External measure relationship readiness workflow" in expander_labels
    assert "Upload external measure audit CSV" in uploader_labels
    assert "External measure audit item response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download external measure audit template" in [
        button.label for button in app.get("download_button")
    ]
    assert "Alternative item-weight sensitivity workflow" in expander_labels
    assert "Upload complete responses for weight sensitivity" in uploader_labels
    assert "Upload alternative weight scheme CSV" in uploader_labels
    assert "Weight sensitivity response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    download_labels = [button.label for button in app.get("download_button")]
    assert "Download complete response template for weight sensitivity" in download_labels
    assert "Download alternative weight scheme template" in download_labels
    assert "Bootstrap sampling uncertainty workflow" in expander_labels
    assert "Upload Bootstrap audit response CSV" in uploader_labels
    assert "Bootstrap audit response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    number_input_labels = [item.label for item in app.number_input]
    assert "Bootstrap resamples" in number_input_labels
    assert "Bootstrap random seed" in number_input_labels
    assert "Bootstrap interval level (%)" in [slider.label for slider in app.slider]
    assert "Download Bootstrap audit response template" in download_labels
    assert "Longitudinal panel readiness workflow" in expander_labels
    assert "Upload longitudinal panel response CSV" in uploader_labels
    assert "Longitudinal panel response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download longitudinal panel response template" in download_labels
    assert "Longitudinal attrition and panel composition workflow" in expander_labels
    assert "Upload attrition audit response CSV" in uploader_labels
    assert "Attrition audit response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download attrition audit response template" in download_labels
    assert "Paired longitudinal Bootstrap uncertainty workflow" in expander_labels
    assert "Upload paired longitudinal Bootstrap response CSV" in uploader_labels
    assert "Paired longitudinal Bootstrap response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Paired longitudinal Bootstrap resamples" in number_input_labels
    assert "Paired longitudinal Bootstrap random seed" in number_input_labels
    assert "Paired longitudinal Bootstrap interval level (%)" in [
        slider.label for slider in app.slider
    ]
    assert "Download paired longitudinal Bootstrap response template" in download_labels
    assert "Longitudinal timing and fieldwork metadata workflow" in expander_labels
    assert "Upload longitudinal timing and fieldwork metadata CSV" in uploader_labels
    assert "Download longitudinal metadata template" in download_labels
    assert "Longitudinal measurement-comparability readiness workflow" in expander_labels
    assert "Upload longitudinal comparability response CSV" in uploader_labels
    assert "Longitudinal comparability response scale" in [
        selectbox.label for selectbox in app.selectbox
    ]
    assert "Download longitudinal comparability response template" in download_labels
    assert "Longitudinal analysis-plan readiness workflow" in expander_labels
    assert "Upload longitudinal analysis-plan CSV" in uploader_labels
    assert "Download longitudinal analysis-plan template" in download_labels
    assert "Longitudinal policy and context event alignment workflow" in expander_labels
    assert "Upload event-alignment round metadata CSV" in uploader_labels
    assert "Upload longitudinal policy and context event CSV" in uploader_labels
    assert "Event exposure definition readiness workflow" in expander_labels
    assert "Upload event exposure-definition CSV" in uploader_labels
    assert "Download event exposure-definition template" in download_labels
    assert "Identification-design readiness workflow" in expander_labels
    assert "Upload identification-design CSV" in uploader_labels
    assert "Download identification-design template" in download_labels
    assert "Falsification and sensitivity plan readiness workflow" in expander_labels
    assert "Upload falsification and sensitivity plan CSV" in uploader_labels
    assert "Download falsification-plan template" in download_labels
    assert "Estimation-specification readiness workflow" in expander_labels
    assert "Upload estimation-specification CSV" in uploader_labels
    assert "Download estimation-specification template" in download_labels
    assert "Download longitudinal event registry template" in download_labels
    assert len(app.get("download_button")) >= 10

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
