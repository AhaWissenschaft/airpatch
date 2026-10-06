"""Ask the model for a change to each task, or load a recorded answer.

Modes (always written into every proposal file and shown in the report):

* LIVE   - a real call to the endpoint in LLM_BASE_URL (Apertus).
* REPLAY - a previously recorded LIVE answer is reused. Never a new result.
* MOCK   - a canned answer from the local test stub. Not a model at all.

Conditions:

* C0 - one answer at temperature 0 (candidate ``c0``).
* C1 - ``k`` independent answers at temperature 0.7 (``s1`` .. ``sk``).
* C2 - repair rounds: after a failed check the model gets the verifier's
  feedback (see feedback.py) and answers again (``r1``, ``r2``, ...).

This step runs in a container that has no access to hidden test cases and
never executes code. The API key lives only in this process's environment.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import feedback, llm
from .tasks import Task, list_tasks, start_files, visible_examples

MODES = ("LIVE", "REPLAY", "MOCK")
SCHEMA = 1
SAMPLE_TEMPERATURE = 0.7

SYSTEM_PROMPT = (
    "You are a careful software engineer. You change small command-line "
    "programs so that they meet their specification. Answer only with the "
    "complete content of every file you change, in the required format."
)


def build_messages(task: Task) -> list[dict]:
    spec = (task.public_dir / "SPEC.md").read_text(encoding="utf-8")
    parts = [f"Task-ID: {task.id}", f"Title: {task.title}", "", "## Specification", spec.strip(), ""]
    parts.append("## Files you may change")
    parts.extend(f"- {p}" for p in task.editable)
    parts.append(f"The program is started as: python3 {task.entry} < input")
    parts.append("")
    parts.append("## Current files")
    for path, content in start_files(task).items():
        parts.extend([f"FILE: {path}", "```python", content.rstrip("\n"), "```", ""])
    examples = visible_examples(task)
    if examples:
        parts.append("## Examples (standard input -> expected standard output)")
        for i, (inp, out) in enumerate(examples, 1):
            parts.extend([f"Example {i} input:", "```", inp.rstrip("\n"), "```",
                          f"Example {i} expected output:", "```", out.rstrip("\n"), "```", ""])
    parts.append("## Answer format")
    parts.append("For every file you change write a line `FILE: <path>` followed by a code "
                 "block with the complete new file content. Write nothing else.")
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "\n".join(parts)}]


def prompt_digest(messages: list[dict], temperature: float) -> str:
    blob = json.dumps({"messages": messages, "temperature": temperature}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


# Upper bound on the prompt tokens of one request, added to the answer limit
# when a call reserves its share of the token cap. Byte-level tokenizers use at
# least one byte of text per token; the per-message and per-request margins
# cover the chat template's role markers and special tokens.
PROMPT_MARGIN_PER_MESSAGE = 32
PROMPT_MARGIN_PER_REQUEST = 256


def token_bound(messages: list[dict], max_answer_tokens: int) -> int:
    """Largest total token count one request with these messages can report."""
    text_bytes = sum(len(m["content"].encode("utf-8")) for m in messages)
    return (text_bytes + PROMPT_MARGIN_PER_MESSAGE * len(messages)
            + PROMPT_MARGIN_PER_REQUEST + max_answer_tokens)


class Budget:
    """Hard caps on model calls and tokens for one run.

    Calls are counted before they are sent. For the token cap every call first
    reserves its upper bound (``token_bound``); a call is refused if the
    tokens already reported plus all open reservations plus its own bound
    would exceed the cap. With parallel calls the cap therefore holds as long
    as the endpoint keeps to ``max_tokens`` and the prompt bound. A call that
    reports more than it reserved is counted with its real usage, recorded as
    an overrun, and stops all further calls.
    """

    def __init__(self, max_calls: int, max_tokens: int | None):
        self.max_calls, self.max_tokens = max_calls, max_tokens
        self.calls = self.tokens = 0
        self.reserved = 0
        self.overruns = 0
        self._lock = threading.Lock()

    def take_call(self, bound: int = 0) -> str | None:
        """Count one call and reserve ``bound`` tokens; returns a refusal or None."""
        with self._lock:
            if self.calls >= self.max_calls:
                return f"call budget of {self.max_calls} reached"
            if self.max_tokens is not None:
                if self.overruns:
                    return "token reservation was exceeded earlier; no further calls"
                if self.tokens + self.reserved + bound > self.max_tokens:
                    return f"token budget of {self.max_tokens} reached"
                self.reserved += bound
            self.calls += 1
            return None

    def settle(self, bound: int, usage: dict | None, *, failed: bool = False) -> bool:
        """Release a reservation and count the real usage. Returns True on an overrun.

        A successful answer without reported usage is counted at its full
        reservation, so the cap still holds. A failed call counts as zero
        tokens (nothing was reported).
        """
        reported = usage.get("total_tokens") if isinstance(usage, dict) else None
        with self._lock:
            if self.max_tokens is not None:
                self.reserved -= bound
            if isinstance(reported, int):
                self.tokens += reported
                if self.max_tokens is not None and reported > bound:
                    self.overruns += 1
                    return True
            elif not failed and self.max_tokens is not None:
                self.tokens += bound
            return False


def _jobs(task: Task, out_dir: Path, feedback_dir: Path | None, samples: int, round_no: int):
    """(candidate, condition, messages, temperature, extra) for one task in this step."""
    base = build_messages(task)
    if round_no == 0:
        yield "c0", "C0", base, 0.0, {}
        for i in range(1, samples + 1):
            yield f"s{i}", "C1", base, SAMPLE_TEMPERATURE, {"sample": i}
        return
    parent = "c0" if round_no == 1 else f"r{round_no - 1}"
    fb_file = (feedback_dir or Path("/nonexistent")) / task.id / f"{parent}.json"
    prev_file = out_dir / task.id / f"{parent}.json"
    if not fb_file.is_file() or not prev_file.is_file():
        return  # the parent passed, or never existed
    fb = json.loads(fb_file.read_text(encoding="utf-8"))
    prev = json.loads(prev_file.read_text(encoding="utf-8"))
    if not prev.get("text"):
        return
    messages = base + [{"role": "assistant", "content": prev["text"]},
                       {"role": "user", "content": feedback.message(fb)}]
    yield f"r{round_no}", "C2", messages, 0.0, {"round": round_no, "parent": parent}


def _one(task: Task, job, mode: str, budget: Budget, cassette_dir: Path | None, env) -> dict:
    candidate, condition, messages, temperature, extra = job
    record = {"schema": SCHEMA, "task": task.id, "candidate": candidate, "condition": condition,
              "source": "model", "mode": mode, "temperature": temperature,
              "prompt_sha256": prompt_digest(messages, temperature), "text": None,
              "usage": None, "latency_ms": None, "model": None, "error": None, **extra}
    if mode == "REPLAY":
        src = (cassette_dir or Path("/nonexistent")) / task.id / f"{candidate}.json"
        if not src.is_file():
            if candidate != "c0":
                return None  # this condition was not recorded; nothing to replay
            record["error"] = "no recorded answer for this task"
            return record
        recorded = json.loads(src.read_text(encoding="utf-8"))
        if recorded.get("mode") != "LIVE":
            raise SystemExit(f"{src}: cassettes may only contain LIVE answers")
        if recorded.get("prompt_sha256") != record["prompt_sha256"]:
            record["error"] = "recorded prompt differs from current prompt"
        record.update({k: recorded.get(k) for k in ("text", "usage", "latency_ms", "model",
                                                     "served_model", "finish_reason")})
        record["recorded_at"] = recorded.get("recorded_at")
        return record
    max_answer = int(env.get("AIRPATCH_MAX_TOKENS", "2048"))
    bound = token_bound(messages, max_answer)
    refusal = budget.take_call(bound)
    if refusal:
        record["error"] = refusal
        return record
    record["model"] = env.get("LLM_NAME", "")
    try:
        answer = llm.chat(env["LLM_BASE_URL"], env["LLM_API_KEY"], record["model"], messages,
                          temperature=temperature, max_tokens=max_answer)
    except llm.LLMError as exc:
        budget.settle(bound, None, failed=True)
        record["error"] = f"model call failed: {exc}"
    else:
        record.update({"text": answer["text"], "usage": answer["usage"],
                       "latency_ms": answer["latency_ms"], "tries": answer["tries"],
                       "finish_reason": answer["finish_reason"], "served_model": answer["served_model"]})
        if budget.settle(bound, None if mode == "MOCK" else answer["usage"]):
            record["token_overrun"] = {"reserved": bound, "reported": answer["usage"]["total_tokens"]}
    if mode == "MOCK":
        record["usage"] = None  # the stub's numbers are not token counts
    if mode == "LIVE":
        record["recorded_at"] = env.get("AIRPATCH_RUN_ID")
    return record


def has_answer(path: Path) -> bool:
    """True if ``path`` holds a usable answer (text and no error) from an earlier attempt."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.get("text") is not None and not data.get("error")


def run(tasks_root: Path, out_dir: Path, kind: str, mode: str, *,
        cassette_dir: Path | None = None, max_calls: int = 64, max_tokens: int | None = None,
        samples: int = 0, round_no: int = 0, feedback_dir: Path | None = None,
        workers: int = 2, env=os.environ, only: set[str] | None = None, resume: bool = False) -> int:
    if mode not in MODES:
        raise SystemExit(f"unknown mode {mode}")
    tasks = [t for t in list_tasks(tasks_root, kind) if not only or t.id in only]
    # The caps hold for the whole run: earlier steps' usage is carried over.
    ledger = out_dir / "_budget.json"
    budget = Budget(max_calls, max_tokens)
    if ledger.is_file():
        used = json.loads(ledger.read_text(encoding="utf-8"))
        budget.calls, budget.tokens = used["calls"], used["tokens"]
        budget.overruns = used.get("overruns", 0)
    work = [(task, job) for task in tasks
            for job in _jobs(task, out_dir, feedback_dir, samples, round_no)]
    if resume:
        # Continue an interrupted step answer by answer: an answer already on disk is kept
        # and never asked again; a missing one (or one that failed) is asked now. The
        # decision is made once, before any call, from the files alone.
        kept = [tj for tj in work if has_answer(out_dir / tj[0].id / f"{tj[1][0]}.json")]
        work = [tj for tj in work if tj not in kept]
        print(f"[{mode}] resume: {len(kept)} answers kept, {len(work)} to ask", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        records = list(pool.map(lambda tj: _one(tj[0], tj[1], mode, budget, cassette_dir, env), work))
    records = [r for r in records if r is not None]
    for record in records:  # written in a fixed order, independent of thread timing
        target = out_dir / record["task"]
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{record['candidate']}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status = "error: " + record["error"] if record["error"] else "ok"
        print(f"[{mode}] {record['task']}/{record['candidate']} ({record['condition']}): {status}", flush=True)
    ledger.write_text(json.dumps({"calls": budget.calls, "tokens": budget.tokens,
                                  "overruns": budget.overruns}) + "\n", encoding="utf-8")
    print(f"[{mode}] {len(records)} answers; run total {budget.calls} model calls, "
          f"{budget.tokens} counted tokens"
          + (f", {budget.overruns} token reservation overrun(s)" if budget.overruns else ""), flush=True)
    return 0
