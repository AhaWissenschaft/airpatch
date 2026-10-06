import heapq
import sys


def main():
    deps = {}
    users = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        name, _, rest = line.partition(":")
        name = name.strip()
        deps.setdefault(name, [])
        users.setdefault(name, set())
        for d in rest.split():
            deps[name].append(d)
            deps.setdefault(d, [])
            users.setdefault(d, set()).add(name)
    waiting = {t: len(ds) for t, ds in deps.items()}
    ready = [t for t, n in waiting.items() if n == 0]
    heapq.heapify(ready)
    while ready:
        t = heapq.heappop(ready)
        print(t)
        del waiting[t]
        for u in users[t]:
            waiting[u] -= 1
            if waiting[u] == 0:
                heapq.heappush(ready, u)
    if waiting:
        print("CYCLE: " + " ".join(sorted(waiting)))


if __name__ == "__main__":
    main()
