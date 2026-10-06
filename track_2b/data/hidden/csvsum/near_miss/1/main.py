import sys


def main():
    totals = {}
    for raw in sys.stdin:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, amount = line.split(",", 1)
        name = name.strip()
        totals[name] = totals.get(name, 0.0) + float(amount)
    for name in sorted(totals):
        print(f"{name} {totals[name]:.2f}")


if __name__ == "__main__":
    main()
