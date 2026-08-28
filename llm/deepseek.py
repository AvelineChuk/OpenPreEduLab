"""Minimal DeepSeek client for researcher-authorised interpretations.

The client uses DeepSeek's OpenAI-compatible chat-completions endpoint.  It
does not read environment variables, persist credentials, or make calls during
initialisation.  A caller must explicitly provide an API key and call
``generate``.
"""

from __future__ import annotations

import json
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEEPSEEK_API_URL: Final = "https://api.deepseek.com/chat/completions"
SUPPORTED_MODELS: Final = ("deepseek-chat", "deepseek-reasoner")


class DeepSeekRequestError(RuntimeError):
    """Raised when DeepSeek cannot return a usable interpretation."""


class DeepSeekClient:
    """Call DeepSeek only with a researcher-provided, session-scoped key.

    Parameters are deliberately explicit so applications can disclose what is
    transmitted.  The key is never stored on disk or included in error text.
    """

    def __init__(self, api_key: str, model: str = "deepseek-chat", timeout_seconds: int = 60) -> None:
        """Initialise a client without making a network request."""
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A non-empty DeepSeek API key is required.")
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported DeepSeek model: {model}.")
        if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
            raise ValueError("timeout_seconds must be a positive integer.")
        self._api_key = api_key.strip()
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Submit supplied prompts and return DeepSeek's text response.

        Only the system prompt and user prompt are transmitted.  HTTP failures
        are converted to a safe error that never exposes the credential.
        """
        payload = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8")
        request = Request(
            DEEPSEEK_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise DeepSeekRequestError(
                "DeepSeek rejected the request. Check your key, account access, model availability, and quota."
            ) from error
        except (URLError, TimeoutError) as error:
            raise DeepSeekRequestError(
                "The request to DeepSeek could not be completed. Check your network connection and try again."
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DeepSeekRequestError("DeepSeek returned an unreadable response.") from error

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise DeepSeekRequestError("DeepSeek returned no interpretation text.") from error
        if not isinstance(content, str) or not content.strip():
            raise DeepSeekRequestError("DeepSeek returned an empty interpretation.")
        return content.strip()
