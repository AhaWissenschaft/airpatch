"""Turn a model answer into a set of file contents.

Expected answer format, one block per changed file::

    FILE: main.py
    ```python
    <complete new content of main.py>
    ```

Anything outside such blocks is ignored. Paths are checked against the
task's list of editable files before anything is written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .tasks import MAX_FILE_BYTES, safe_relpath

MAX_BLOCKS = 8

_BLOCK = re.compile(
    r"^FILE:[ \t]*(?P<path>[^\n]*?)[ \t]*\n"  # header line
    r"```[^\n]*\n"  # opening fence, optional language tag
    r"(?P<body>.*?)"  # file content (non-greedy)
    r"^```[ \t]*$",  # closing fence on its own line
    re.MULTILINE | re.DOTALL,
)
_FENCE = re.compile(r"^```[^\n]*\n(?P<body>.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)


@dataclass
class ParsedProposal:
    files: dict[str, str] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def status(self) -> str:
        if self.violations:
            return "POLICY_VIOLATION"
        if self.error:
            return "MALFORMED_PROPOSAL"
        return "OK"


def parse(text: str, editable: tuple[str, ...]) -> ParsedProposal:
    result = ParsedProposal()
    blocks = [(m.group("path"), m.group("body")) for m in _BLOCK.finditer(text)]
    if not blocks:
        fences = _FENCE.findall(text)
        if len(fences) == 1 and len(editable) == 1:
            # Lenient path: a single code block for a single editable file.
            blocks = [(editable[0], fences[0])]
        else:
            result.error = "no FILE block found"
            return result
    if len(blocks) > MAX_BLOCKS:
        result.error = f"more than {MAX_BLOCKS} FILE blocks"
        return result
    for path_text, body in blocks:
        path = safe_relpath(path_text.strip().strip("`"))
        if path is None:
            result.violations.append(f"unsafe path: {path_text[:80]!r}")
            continue
        if path not in editable:
            result.violations.append(f"path not editable: {path[:80]!r}")
            continue
        if path in result.files:
            result.error = f"duplicate FILE block for {path}"
            continue
        if len(body.encode("utf-8")) > MAX_FILE_BYTES:
            result.error = f"file too large: {path}"
            continue
        result.files[path] = body
    return result
