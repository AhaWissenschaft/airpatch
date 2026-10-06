import sys


def round_cents(num, den):
    """num / den (den > 0) rounded to two decimals, halves away from zero."""
    sign = "-" if num < 0 else ""
    cents = (200 * abs(num) + den) // (2 * den)
    if cents == 0:
        sign = ""
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def half(twice):
    """twice / 2, printed as an integer or with .5."""
    if twice % 2 == 0:
        return str(twice // 2)
    return ("-" if twice < 0 else "") + f"{abs(twice) // 2}.5"


def main():
    values = [int(tok) for tok in sys.stdin.read().split()]
    n = len(values)
    print("count", n)
    if not n:
        return
    print("mean", f"{sum(values) / n:.2f}")
    s = sorted(values)
    if n % 2:
        print("median", s[n // 2])
    else:
        print("median", half(s[n // 2 - 1] + s[n // 2]))
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    best = max(counts.values())
    print("mode", min(v for v, c in counts.items() if c == best))
    print("range", s[-1] - s[0])


if __name__ == "__main__":
    main()
