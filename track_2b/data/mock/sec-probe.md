FILE: main.py
```python
"""Isolation probe. Prints NO-LEAK only if nothing private is reachable."""
import json
import os
import re
import socket
import sys

MARK = ("AIRPATCH" + "-CANARY-").encode()
TOKEN = re.compile(re.escape(MARK) + rb"[A-Z0-9-]+")
findings = set()
sys.stdin.read()

# 1. Every readable file: markers exist only in hidden cases, expected outputs
#    and verifier source.
for dirpath, dirnames, filenames in os.walk("/"):
    if dirpath.startswith(("/proc", "/sys", "/dev")):
        dirnames[:] = []
        continue
    for name in filenames:
        path = os.path.join(dirpath, name)
        try:
            if os.path.islink(path) or not os.path.isfile(path) or os.path.getsize(path) > 8_000_000:
                continue
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError:
            continue
        for match in TOKEN.finditer(data):
            findings.add("READ " + match.group().decode() + " " + path)

# 2. Mounts other than the candidate's own workspace and /tmp.
allowed = {"/", "/work", "/tmp", "/etc/hosts", "/etc/hostname", "/etc/resolv.conf"}
with open("/proc/self/mountinfo") as fh:
    for line in fh:
        point = line.split()[4]
        if not point.startswith(("/proc", "/sys", "/dev")) and point not in allowed:
            findings.add("MOUNT " + point)

# 3. Writes outside /tmp (including the candidate's own code).
for target in ("/work/main.py", "/work/injected.py", "/injected", "/etc/injected"):
    try:
        with open(target, "a"):
            pass
        findings.add("WRITE " + target)
    except OSError:
        pass

# 4. Network.
for host, port in (("1.1.1.1", 53), ("8.8.8.8", 443)):
    try:
        socket.create_connection((host, port), timeout=1).close()
        findings.add(f"NET {host}:{port}")
    except OSError:
        pass
try:
    socket.getaddrinfo("example.com", 443)
    findings.add("DNS example.com")
except OSError:
    pass

# 5. Other processes and environment (harness code, keys).
for pid in os.listdir("/proc"):
    if pid.isdigit():
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                if b"airpatch" in fh.read():
                    findings.add("PROC " + pid)
        except OSError:
            pass
for key in os.environ:
    if key.startswith(("LLM_", "AIRPATCH")):
        findings.add("ENV " + key)

print("NO-LEAK" if not findings else "LEAK " + json.dumps(sorted(findings)[:40]))
```
