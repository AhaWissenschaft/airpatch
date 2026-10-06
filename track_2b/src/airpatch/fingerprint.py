"""Stable fingerprints of error messages.

Two runs of the same failing program should produce the same fingerprint even
if memory addresses or absolute paths differ, so errors can be compared and
counted across runs.
"""

from __future__ import annotations

import hashlib
import re

_RULES = [
    (re.compile(r"0x[0-9a-fA-F]+"), "0xADDR"),
    (re.compile(r"/work/"), "<work>/"),
    (re.compile(r"/tmp/[^\s'\"]*"), "<tmp>"),
    (re.compile(r"[ \t]+$", re.MULTILINE), ""),
]
TAIL_LINES = 20


def normalise(text: str) -> str:
    for pattern, repl in _RULES:
        text = pattern.sub(repl, text)
    lines = [line for line in text.replace("\r\n", "\n").split("\n") if line.strip()]
    return "\n".join(lines[-TAIL_LINES:])


def fingerprint(text: str) -> str | None:
    norm = normalise(text)
    if not norm:
        return None
    return hashlib.sha256(norm.encode("utf-8", "replace")).hexdigest()[:16]


def final_line(text: str, limit: int = 200) -> str:
    norm = normalise(text)
    return norm.split("\n")[-1][:limit] if norm else ""
