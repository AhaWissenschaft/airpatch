"""Static checks of the launcher's container options."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "scripts" / "airpatch.sh"


def invocations(text: str) -> list[str]:
    """Every `docker run` / `harness` call, joined across line continuations."""
    joined = re.sub(r"\\\n\s*", " ", text)
    calls = []
    for line in joined.splitlines():
        line = line.strip()
        if line.startswith("#") or line.startswith("harness()"):
            continue
        for m in re.finditer(r"(?:docker run|(?<![\w-])harness) ", line):
            calls.append(line[m.start():])
    return calls


class LauncherConfigTests(unittest.TestCase):
    def setUp(self):
        self.text = LAUNCHER.read_text(encoding="utf-8")
        self.calls = invocations(self.text)

    def test_found_the_calls(self):
        self.assertGreater(len(self.calls), 15)

    def test_every_container_has_an_explicit_network(self):
        for call in self.calls:
            if call.startswith("docker run $H"):
                continue  # the harness() wrapper itself; callers pass --network
            self.assertRegex(call, r"--network ", call[:120])

    def test_only_the_live_proposer_reaches_the_network(self):
        bridged = [c for c in self.calls if "--network bridge" in c]
        self.assertEqual(len(bridged), 1)
        self.assertIn("--mode LIVE", bridged[0])
        for call in self.calls:
            self.assertNotRegex(call, r"--network (host|default)\b")

    def test_no_privilege_escalation_options(self):
        for forbidden in ("docker.sock", "--privileged", "--cap-add", "--pid host", "--pid=host",
                          "seccomp=unconfined", "apparmor=unconfined"):
            self.assertNotIn(forbidden, self.text)

    def test_candidate_containers_are_hardened(self):
        cand = [c for c in self.calls if "python3 -I -B" in c and "$BASE_IMAGE" in c]
        self.assertGreaterEqual(len(cand), 2)
        for call in cand:
            for opt in ("--network none", "--read-only", "--cap-drop ALL", "no-new-privileges",
                        "--pids-limit", "--memory", "--user 65534:65534"):
                self.assertIn(opt, call)

    def test_hidden_data_is_never_mounted_into_propose_or_candidates(self):
        for call in self.calls:
            if " propose " in call or 'python3 -I -B "/work/$entry"' in call:
                self.assertNotIn("data/hidden", call, call[:120])


if __name__ == "__main__":
    unittest.main()
