"""A tiny stand-in for an OpenAI-compatible endpoint, used for tests and demos.

It returns a canned answer per task (``<mock_dir>/<task-id>.md``). It is not a
model and its answers are always labelled MOCK.
"""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .tasks import TASK_ID

_TASK_LINE = re.compile(r"^Task-ID: (\S+)$", re.MULTILINE)
FALLBACK = "I cannot solve this task."


def answer_for(mock_dir: Path, messages: list) -> str:
    """Canned answer: ``<task>.md``, or ``<task>.r<N>.md`` in repair round N if present."""
    text = "\n".join(m.get("content", "") for m in messages if isinstance(m, dict))
    match = _TASK_LINE.search(text)
    if not match or not TASK_ID.fullmatch(match.group(1)):
        return FALLBACK
    round_no = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "assistant")
    if round_no:
        path = mock_dir / f"{match.group(1)}.r{round_no}.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    path = mock_dir / f"{match.group(1)}.md"
    return path.read_text(encoding="utf-8") if path.is_file() else FALLBACK


def handler_class(mock_dir: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # keep test output quiet  # noqa: A002
            pass

        def _send(self, code: int, body: dict) -> None:
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(200 if self.path == "/health" else 404, {"ok": self.path == "/health"})

        def do_POST(self):
            if not self.path.endswith("/chat/completions"):
                self._send(404, {"error": "not found"})
                return
            try:
                length = max(0, min(int(self.headers.get("Content-Length", "0")), 1 << 20))
                req = json.loads(self.rfile.read(length))
                messages = req["messages"]
            except (ValueError, KeyError, TypeError):  # JSONDecodeError is a ValueError
                self._send(400, {"error": "bad request"})
                return
            if req.get("model") == "fail-503":  # lets tests exercise error handling
                self._send(503, {"error": "unavailable"})
                return
            content = answer_for(mock_dir, messages)
            prompt_chars = sum(len(m.get("content", "")) for m in messages if isinstance(m, dict))
            self._send(200, {
                "model": "mock",
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": content}}],
                # Character counts / 4: a stand-in, never reported as real token usage.
                "usage": {"prompt_tokens": prompt_chars // 4, "completion_tokens": len(content) // 4,
                          "total_tokens": (prompt_chars + len(content)) // 4},
            })

    return Handler


def serve(mock_dir: Path, port: int) -> None:
    server = ThreadingHTTPServer(("0.0.0.0", port), handler_class(mock_dir))
    print(f"mockllm listening on :{port}", flush=True)
    server.serve_forever()
