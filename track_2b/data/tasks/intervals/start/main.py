import sys


def main():
    intervals = [tuple(map(int, line.split())) for line in sys.stdin if line.strip()]
    merged = []
    for a, b in intervals:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    for a, b in merged:
        print(a, b)


if __name__ == "__main__":
    main()
