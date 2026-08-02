"""Unit tests for the optional DeepSeek client; no external API call is made."""

import json

import pytest

from llm.deepseek import DeepSeekClient, DeepSeekRequestError


def test_deepseek_client_rejects_missing_key() -> None:
    """Credentials must be supplied explicitly by the researcher."""
    with pytest.raises(ValueError, match="API key"):
        DeepSeekClient("")


def test_deepseek_client_rejects_unknown_model() -> None:
    """Only deliberately supported model identifiers may be selected."""
    with pytest.raises(ValueError, match="Unsupported"):
        DeepSeekClient("test-key", model="unknown-model")


def test_deepseek_client_returns_content_without_exposing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful OpenAI-compatible payload is converted to plain text."""
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps({"choices": [{"message": {"content": "Bounded interpretation."}}]}).encode()

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("llm.deepseek.urlopen", fake_urlopen)
    client = DeepSeekClient("private-test-key")

    assert client.generate("system", "evidence") == "Bounded interpretation."
    assert captured["timeout"] == 60


def test_deepseek_client_uses_safe_error_for_transport_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Transport errors must not leak credential values."""
    from urllib.error import URLError

    def failing_urlopen(*args: object, **kwargs: object) -> object:
        raise URLError("offline")

    monkeypatch.setattr("llm.deepseek.urlopen", failing_urlopen)
    with pytest.raises(DeepSeekRequestError, match="could not be completed"):
        DeepSeekClient("private-test-key").generate("system", "evidence")
