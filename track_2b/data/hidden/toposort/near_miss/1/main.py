import sys
from collections import deque


def main():
    deps = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        name, _, rest = line.partition(":")
        name = name.strip()
        deps.setdefault(name, set()).update(rest.split())
        for d in rest.split():
            deps.setdefault(d, set())
    waiting = {t: len(ds) for t, ds in deps.items()}
    users = {t: [] for t in deps}
    for t, ds in deps.items():
        for d in ds:
            users[d].append(t)
    ready = deque(sorted(t for t, n in waiting.items() if n == 0))
    while ready:
        t = ready.popleft()
        print(t)
        del waiting[t]
        for u in users[t]:
            waiting[u] -= 1
            if waiting[u] == 0:
                ready.append(u)
    if waiting:
        print("CYCLE: " + " ".join(sorted(waiting)))


if __name__ == "__main__":
    main()
