import re
import sys


def main():
    words = {w.lower() for w in re.findall(r"[A-Za-z]+", sys.stdin.read())}
    groups = {}
    for word in words:
        groups.setdefault("".join(sorted(word)), []).append(word)
    found = [sorted(groups[k]) for k in sorted(groups) if len(groups[k]) >= 2]
    found.sort(key=len, reverse=True)
    for g in found:
        print(" ".join(g))


if __name__ == "__main__":
    main()
