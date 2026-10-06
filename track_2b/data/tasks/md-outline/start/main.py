import sys


def main():
    counters = [0] * 6
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line.startswith("#"):
            continue
        level = len(line) - len(line.lstrip("#"))
        text = line[level:].strip()
        counters[level - 1] += 1
        for i in range(level, 6):
            counters[i] = 0
        number = ".".join(str(c) for c in counters[:level])
        slug = text.lower().replace(" ", "-")
        print("  " * (level - 1) + f"{number} {text} (#{slug})")


if __name__ == "__main__":
    main()
