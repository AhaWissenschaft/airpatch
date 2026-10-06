import re
import sys


def main():
    words = {w.lower() for w in re.findall(r"[A-Za-z]+", sys.stdin.read())}
    groups = {}
    for word in words:
        groups.setdefault("".join(sorted(word)), []).append(word)
    found = [sorted(g) for g in groups.values() if len(g) >= 2]
    found.sort(key=lambda g: (-len(g), g[0]))
    for g in found:
        print(" ".join(g))


if __name__ == "__main__":
    main()
