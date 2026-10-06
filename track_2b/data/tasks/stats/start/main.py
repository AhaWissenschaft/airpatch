import sys


def main():
    values = [int(x) for x in sys.stdin.read().split()]
    n = len(values)
    print("count", n)
    print("mean", f"{sum(values) / n:.2f}")
    s = sorted(values)
    print("median", s[n // 2])
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    print("mode", max(counts, key=counts.get))
    print("range", max(values) - min(values))


if __name__ == "__main__":
    main()
