import sys


def main():
    groups = {}
    for word in sys.stdin.read().split():
        word = word.lower()
        groups.setdefault("".join(sorted(word)), []).append(word)
    for key in sorted(groups):
        if len(groups[key]) > 1:
            print(" ".join(sorted(groups[key])))


if __name__ == "__main__":
    main()
