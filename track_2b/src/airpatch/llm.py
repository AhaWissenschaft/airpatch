"""Minimal client for an OpenAI-compatible chat completions endpoint.

Standard library only. The API key is sent in the Authorization header and is
never logged, stored or included in error messages.
"""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504}


class LLMError(Exception):
    def __init__(self, message: str, *, status: int | None = None, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.retryable = retryable


def chat_url(base_url: str) -> str:
    """Build the chat completions URL from LLM_BASE_URL.

    Accepts a base ending in ``/v1``, a full ``.../chat/completions`` URL, or a
    bare host (``/v1`` is then added).
    """
    base = base_url.strip().rstrip("/")
    parts = urlsplit(base)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise LLMError("LLM_BASE_URL must be an http(s) URL")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def _post(url: str, api_key: str, payload: dict, timeout_s: float, opener) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + api_key)
    try:
        with opener(req, timeout=timeout_s) as resp:
            body = resp.read(4 * 1024 * 1024)
    except urllib.error.HTTPError as exc:
        exc.close()  # release the connection; the status code is all we keep
        raise LLMError(f"HTTP {exc.code}", status=exc.code,
                       retryable=exc.code in RETRYABLE_STATUS) from None
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
        reason = getattr(exc, "reason", exc)
        raise LLMError(f"connection failed: {type(reason).__name__}", retryable=True) from None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise LLMError("response is not JSON") from None


def chat(base_url: str, api_key: str, model: str, messages: list[dict], *,
         temperature: float = 0.0, max_tokens: int = 2048, timeout_s: float = 180.0,
         retries: int = 2, retry_wait_s: float = 2.0, opener=urllib.request.urlopen) -> dict:
    """Send one chat request. Returns text, usage (or None), latency and attempt count."""
    url = chat_url(base_url)
    payload = {"model": model, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens}
    tries = 0
    while True:
        tries += 1
        started = time.monotonic()
        try:
            body = _post(url, api_key, payload, timeout_s, opener)
            break
        except LLMError as exc:
            if not exc.retryable or tries > retries:
                raise
            time.sleep(retry_wait_s * (2 ** (tries - 1)))
    latency_ms = int((time.monotonic() - started) * 1000)
    try:
        choice = body["choices"][0]
        text = choice["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise LLMError("response has no choices[0].message.content") from None
    usage = body.get("usage") if isinstance(body.get("usage"), dict) else None
    return {"text": text, "usage": usage, "latency_ms": latency_ms, "tries": tries,
            "finish_reason": choice.get("finish_reason"),
            "served_model": body.get("model")}
